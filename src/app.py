from flask import Flask, request, flash, session, redirect, render_template, url_for, jsonify, make_response, Response
# OrderedDict used by reports
# leave this import
from collections import OrderedDict
import datetime
from datetime import timedelta
from flask.ext.session import Session
from functools import wraps
from utils import conversions, deep_update, is_num, gen_nested_dict, User, format_errors
from logger import ilogger as logger
import requests
import json
import PyRSS2Gen
import os
import base64


espaweb = Flask(__name__)
espaweb.config.from_envvar('ESPAWEB_SETTINGS', silent=False)
espaweb.secret_key = espaweb.config['SECRET_KEY']
espaweb.config['SESSION_TYPE'] = 'memcached'
espaweb.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=120)

Session(espaweb)
api_base_url = "http://{0}:{1}/api/{2}".format(espaweb.config['APIHOST'],
                                               espaweb.config['APIPORT'],
                                               espaweb.config['APIVERSION'])


def api_get(url, response_type='json', json=None, uauth=None):
    auth_tup = uauth if uauth else (session['user'].username, session['user'].wurd)
    response = requests.get(api_base_url + url, auth=auth_tup, json=json)
    if response_type == 'json':
        _resp = response.json()
    elif response_type == 'text':
        _resp = response.text
    else:
        _resp = response
    return _resp


def api_up(url, json, verb='post'):
    auth_tup = (session['user'].username, session['user'].wurd)
    if verb not in ('post', 'put'):
        return {'message': 'api verb not found: {}'.format(verb)}, 404
    response = getattr(requests, verb)(api_base_url + url, json=json, auth=auth_tup)
    return response


def update_status_details():
    status_response = api_get('/system-status')
    for item in ['system_message_body', 'system_message_title', 'display_system_message']:
        session[item] = status_response[item]

    for item in ['stat_products_complete_24_hrs', 'stat_backlog_depth']:
        session[item] = api_get('/statistics/' + item, 'text')


def staff_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        is_staff = False
        if 'user' in session:
            is_staff = session['user'].is_staff

        if is_staff is False:
            flash('staff only', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or session['logged_in'] is not True:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def request_wants_json():
    return 'Content-Type' in request.headers and request.headers['Content-Type'] == 'application/json'


@espaweb.route('/login', methods=['GET', 'POST'])
def login():
    destination = request.args.get('next')
    if request.method == 'POST':
        resp_json = api_get("/user", uauth=(request.form['username'], request.form['password']))
        if 'username' in resp_json:
            session['logged_in'] = True
            resp_json['wurd'] = request.form['password']
            session['user'] = User(**resp_json)
            update_status_details()
            logger.info("User %s logged in\n" % session['user'].username)
            # send the user back to their
            # originally requested destination
            if destination and destination != 'None':
                return redirect(destination)
            else:
                return redirect(url_for('index'))
        else:
            logger.info("**** Failed user login %s \n" % request.form['username'])
            flash(format_errors(resp_json['msg']), 'error')
            _status = 401
    else:
        _status = 200
        if 'user' not in session:
            session['user'] = None

    in_ops = 'ESPA_ENV' in os.environ and os.environ['ESPA_ENV'] == 'ops'
    explorer = "http://earthexplorer.usgs.gov" if in_ops else "http://eedevmast.cr.usgs.gov"
    reg_host = "https://ers.cr.usgs.gov" if in_ops else "http://ersdevmast.cr.usgs.gov"

    return render_template('login.html', next=destination,
                           earthexplorer=explorer,
                           register_user=reg_host+"/register",
                           forgot_login=reg_host+"/password/request"), _status


@espaweb.route('/logout')
def logout():
    logger.info("Logging out user %s \n" % session['user'].username)
    for item in ['logged_in', 'user', 'system_message_body', 'system_message_title',
                 'stat_products_complete_24_hrs', 'stat_backlog_depth']:
        session.pop(item, None)
    return redirect(url_for('login'))


@espaweb.route('/')
@espaweb.route('/index/')
@login_required
def index():
    return render_template('index.html')


@espaweb.route('/ordering/new/')
@login_required
def new_order():
    return render_template('new_order.html', form_action=url_for('submit_order'))


@espaweb.route('/ordering/new_external/', methods=['GET','POST'])
def new_external_order():
    if request.method == 'POST':
        data = request.form.to_dict()
        try:
            scenelist = data['input_product_list']
            _u, _p = base64.b64decode(data['user']).split(':')
            resp_json = api_get('/user', uauth=(_u, _p))
            if 'username' in resp_json:
                session['logged_in'] = True
                resp_json['wurd'] = _p
                session['user'] = User(**resp_json)
            else:
                logger.info('*** Failed external order user login: {}'.format(_u))
                return jsonify({'msg': 'user auth failed'}), 401
        except KeyError:
            return jsonify({'error': "'input_product_list' and 'user' fields are required"}), 401
        except Exception as e:
            logger.info("*** espa-web exception - problem parsing external order request. message: {}".format(e.message))
            return jsonify({'error': 'problem parsing request'}), 400
    else:
        # GET redirect from ESPA after order validation
        scenelist = session['ipl']

    return render_template('new_order.html',
                           form_action=url_for('submit_order'),
                           scenelist=scenelist)


@espaweb.route('/foo/', methods=['GET'])
def get_foo():
    resp = make_response(render_template('foo.html'))
    return resp


@espaweb.route('/ordering/submit/', methods=['POST'])
@login_required
def submit_order():
    # form values come in as an ImmutableMultiDict
    data = request.form.to_dict()
    logger.info("* new order submission for user %s\n\n order details: %s\n\n\n" % (session['user'].username, data))
    _external = False
    try:
        # grab sceneids from the file in input_product_list field
        _ipl_list = request.files.get('input_product_list').read().splitlines()
        _ipl = [i.strip().split("/r") for i in _ipl_list]
        _ipl = [item for sublist in _ipl for item in sublist if item]
    except AttributeError, e:
        # must be coming from new_external_order
        _ipl_list = data.pop('input_product_list')
        _ipl = _ipl_list.split(",")
        session['ipl'] = _ipl_list
        _external = True

    try:
        # convert our list of sceneids into format required for new orders
        scene_dict_all_prods = api_up("/available-products", {'inputs': _ipl}).json()
    except UnicodeDecodeError as e:
        flash('Decoding Error with input file. Please check input file encoding', 'error')
        logger.info("problem with order submission for user %s\n\n message: %s\n\n" % (session['user'].username,
                                                                                       e.message))

        return redirect(url_for('new_order'))


    # create a list of requested products
    landsat_list = [key for key in data if key in conversions['products']]
    # now that we have the product list, lets remove
    # this key from the form inputs
    for p in landsat_list:
        data.pop(p)

    # the image extents parameters also come in under
    # this key in the form, and this causes a conflict
    # with the 'image_extents' used to enable modifying
    # image extents in the deep_update function
    clk = ['image_extents', 'projection', 'resize']
    for k in clk:
        if k in data:
            # 'image_extents', 'projection', 'resize'
            # are in data.keys().  if there are child
            # keys, remove k
            if "{}|".format(k) in " ".join(data.keys()):
                data.pop(k)
        else:
            # project, resize, image_extents are not there
            # so remove their children
            for key in data.keys():
                if k in key:
                    data.pop(key)

    # this dictionary will hold the output
    out_dict = {}
    for k, v in data.iteritems():
        # all values coming in from the post request
        # are unicode, convert those values which
        # should be int or float
        tdict = gen_nested_dict(k.split("|"), is_num(v))
        # deep_update updates the dictionary
        deep_update(out_dict, tdict)

    # MODIS only receive l1 or stats
    modis_list = ['l1']
    if 'stats' in landsat_list:
        modis_list.append('stats')

    # we dont need these values returned by the available-products query
    if 'date_restricted' in scene_dict_all_prods:
        scene_dict_all_prods.pop('date_restricted')

    for key in scene_dict_all_prods:
            if 'mod' in key or 'myd' in key:
                scene_dict_all_prods[key]['products'] = modis_list
            elif key not in ('not_implemented', 'date_restricted'):
                # Probably better to let the user know if there
                # are invalid landsat/product combinations rather than
                # just making them disappear from the order, MODIS
                # being the exception
                scene_dict_all_prods[key]['products'] = landsat_list

    # combine order options with product lists
    out_dict.update(scene_dict_all_prods)

    # keys to clean up
    cleankeys = ['not_implemented', 'target_projection', 'date_restricted']
    for item in cleankeys:
        if item in out_dict:
            if item == 'target_projection' and out_dict[item] == 'lonlat':
                # there are no other parameters needed for a geographic
                # projection, so assign 'lonlat' to the projection key
                out_dict['projection'] = {'lonlat': None}
            out_dict.pop(item)

    if 'plot_statistics' in out_dict:
        out_dict['plot_statistics'] = True

    logger.info('Order out to API: {}'.format(out_dict))
    response = api_up("/order", out_dict)
    response_data = response.json()
    logger.info('Response from API: {}'.format(response_data))

    # hack till we settle on msg or message
    if 'message' in response_data:
        response_data['msg'] = response_data['message']

    if response.status_code == 200:
        flash("Order submitted successfully! Your OrderId is {}".format(response_data['orderid']))
        logger.info("successful order submission for user %s\n\n orderid: %s" % (session['user'].username,
                                                                                 response_data['orderid']))
        rdest = redirect('/ordering/order-status/{}/'.format(response_data['orderid']))
    else:
        flash(format_errors(response_data["msg"]), 'error')
        logger.info("problem with order submission for user %s\n\n message: %s\n\n" % (session['user'].username,
                                                                                       response_data['msg']))
        _dest = url_for('new_external_order') if _external else url_for('new_order')
        rdest = redirect(_dest)

    return rdest


@espaweb.route('/ordering/status/')
@espaweb.route('/ordering/status/<email>/')
@login_required
def list_orders(email=None):
    url = "/list-orders-ext"
    for_user = session['user'].email
    if email:
        url += "/{}".format(email)
        for_user = email
    res_data = api_get(url, json={'status': ['complete', 'ordered']})
    if isinstance(res_data, list):
        res_data = sorted(res_data, key=lambda k: k['orderid'], reverse=True)

    return render_template('list_orders.html', order_list=res_data, for_user=for_user)


@espaweb.route('/ordering/status/<email>/rss/')
def list_orders_feed(email):
    # bulk downloader and the browser hit this url, need to handle
    # user auth for both use cases
    url = "/list-orders-feed/{}".format(email)
    if 'Authorization' in request.headers:
        # coming in from bulk downloader
        logger.info("Apparent bulk download attempt, headers: %s" % request.headers)
        auth_header_dec = base64.b64decode(request.headers['Authorization'])
        response = api_get(url, uauth=tuple(auth_header_dec.split(":")))
    else:
        if 'logged_in' not in session or session['logged_in'] is not True:
            return redirect(url_for('login', next=request.url))
        else:
            response = api_get(url)

    if "msg" in response:
        logger.info("Problem retrieving rss for email: %s \n message: %s\n" % (email, response['msg']))
        status_code = 404
        if "Invalid username/password" in response['msg']:
            status_code = 403
        return jsonify(response), status_code
    else:
        rss = PyRSS2Gen.RSS2(
            title='ESPA Status Feed',
            link='http://espa.cr.usgs.gov/ordering/status/{0}/rss/'.format(email),
            description='ESPA scene status for:{0}'.format(email),
            language='en-us',
            lastBuildDate=datetime.datetime.now(),
            items=[]
        )

        for item in response:
            for scene in response[item]['scenes']:
                description = 'scene_status:{0},orderid:{1},orderdate:{2}'.format(scene['status'], item, response[item]['orderdate'])
                new_rss_item = PyRSS2Gen.RSSItem(
                    title=scene['name'],
                    link=scene['url'],
                    description=description,
                    guid=PyRSS2Gen.Guid(scene['url'])
                )

                rss.items.append(new_rss_item)

        return rss.to_xml(encoding='utf-8')


@espaweb.route('/ordering/order-status/<orderid>/')
@login_required
def view_order(orderid):
    order_dict = api_get("/order/{}".format(orderid))
    scenes_resp = api_get("/item-status/{}".format(orderid))

    scenes = scenes_resp['orderid'][orderid]

    statuses = {'complete': ['complete', 'unavailable'],
                'open': ['oncache', 'queued', 'processing', 'error', 'submitted'],
                'waiting': ['retry', 'onorder'],
                'error': ['error']}

    product_counts = {}
    for status in statuses:
        product_counts[status] = len([s for s in scenes if s['status'] in statuses[status]])
    product_counts['total'] = len(scenes)

    # get away from unicode
    joptions = json.dumps(order_dict['product_opts'])

    # sensor/products
    options_by_sensor = {}
    for key in order_dict['product_opts']:
        _kval = order_dict['product_opts'][key]
        if isinstance(_kval, dict) and 'products' in _kval:
            _spl = _kval['products']
            _out_spl = [conversions['products'][item] for item in _spl]
            options_by_sensor[key] = _out_spl

    options_list = [" {0}: {1} ,".format(sensor, ", ".join(options_by_sensor[sensor])) for sensor in options_by_sensor]
    options_str = " ".join(options_list)

    return render_template('view_order.html', order=order_dict, scenes=scenes, prod_str=options_str,
                           product_counts=product_counts, product_opts=joptions)


@espaweb.route('/reports/')
@staff_only
@login_required
def list_reports():
    res_data = api_get("/reports/")
    return render_template('list_reports.html', reports=res_data)


@espaweb.route('/reports/<name>/')
@staff_only
@login_required
def show_report(name):
    response = api_get("/reports/{0}/".format(name))
    res_data = eval(response)
    # occassionally see UnicodeDecodeError in reports
    # lets decode the response
    for rpt in res_data:
      for k,v in rpt.items():
        rpt[k] = str(v).decode('utf8', 'strict')
    return render_template('report.html', report_name=name, report=res_data)


@espaweb.route('/console', methods=['GET'])
@staff_only
@login_required
def console():
    data = api_get("/statistics/all")
    stats = {'Open Orders': data['stat_open_orders'],
             'Products Complete 24hrs': data['stat_products_complete_24_hrs'],
             'Waiting Users': data['stat_waiting_users'],
             'Backlog Depth': data['stat_backlog_depth']}
    return render_template('console.html', stats=stats)


@espaweb.route('/console/statusmsg', methods=['GET', 'POST'])
@staff_only
@login_required
def statusmsg():
    if request.method == 'POST':
        dsm = 'True' if 'display_system_message' in request.form else 'False'
        api_args = {'system_message_title': request.form['system_message_title'],
                    'system_message_body': request.form['system_message_body'],
                    'display_system_message': dsm}
        response = api_up('/system-status-update', api_args)

        if response.status_code == 200:
            update_status_details()
            flash('update successful')
            rurl = 'index'
        else:
            flash('update failed', 'error')
            rurl = 'statusmsg'
        action = redirect(url_for(rurl))
    else:
        update_status_details()
        action = render_template('statusmsg.html')

    return action


@espaweb.route('/console/config', methods=['GET'])
@staff_only
@login_required
def console_config():
    config_data = api_get("/system/config")
    sorted_keys = sorted(config_data)
    return render_template('config.html', config_data=config_data, sorted_keys=sorted_keys)


@espaweb.route('/adm/<action>/<orderid>', methods=['PUT'])
@staff_only
@login_required
def admin_update(action, orderid):
    return api_up('/{}/{}'.format(action, orderid), {}, 'put').text

if __name__ == '__main__':
    debug = False
    if 'ESPA_DEBUG' in os.environ and os.environ['ESPA_DEBUG'] == 'True':
        debug = True
    espaweb.run(debug=debug, use_evalex=False, host='0.0.0.0', port=8889)

