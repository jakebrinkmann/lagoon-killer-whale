from flask import Flask, request, flash, session, redirect, render_template, url_for
# OrderedDict and datetime used by reports, leave
from collections import OrderedDict
import datetime
from datetime import timedelta
from flask.ext.session import Session
from werkzeug.datastructures import ImmutableMultiDict
from functools import wraps
from user import User
from utils import conversions, deep_update
import requests
import json

app = Flask(__name__)
app.config.from_envvar('ESPAWEB_SETTINGS', silent=False)
app.secret_key = '@ijn@@d)h@8f8avh+h=lzed2gy=hp2w+6+nbgl2sdyh$!x!%3+'
app.config['SESSION_TYPE'] = 'memcached'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

Session(app)
api_base_url = "http://{0}:{1}".format(app.config['APIHOST'], app.config['APIPORT'])

def is_num(value):
    try:
        # is it an int
        rv = int(value)
    except:
        try:
            # is it a float
            rv = float(value)
        except:
            # must be a str
            rv = value
    return rv

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session.keys():
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    user = None
    next = request.args.get('next')

    if request.method == 'POST':
        auth_url = api_base_url + "/api/v0/user"
        response = requests.get(auth_url, auth=(request.form['username'], request.form['password']))
        resp_json = response.json()
        resp_json['wurd'] = request.form['password']
        user = User(**resp_json)
        if response.status_code == 200:
            session['logged_in'] = True
            session['user'] = user

            status_response = requests.get(api_base_url + '/api/v0/system-status',
                                           auth=(user.username, user.wurd))
            sys_msg_resp = status_response.json()
            session['system_message_body'] = sys_msg_resp['system_message_body']
            session['system_message_title'] = sys_msg_resp['system_message_title']
            session['display_system_message'] = sys_msg_resp['display_system_message']
            session['stat_products_complete_24_hrs'] = requests.get(api_base_url+'/api/v0/statistics/stat_products_complete_24_hrs',
                                                                    auth=(user.username, user.wurd)).text
            session['stat_backlog_depth'] = requests.get(api_base_url + '/api/v0/statistics/stat_backlog_depth',
                                              auth=(user.username, user.wurd)).text

            # send the user back to their
            # originally requested destination
            if next and next != 'None':
                return redirect(next)
            else:
                return redirect(url_for('index'))

        else:
            error = resp_json['msg']
    return render_template('login.html', error=error, user=user, next=next)

@app.route('/logout')
def logout():
    for item in ['logged_in', 'user', 'system_message_body', 'system_message_title',
                 'stat_products_complete_24_hrs', 'stat_backlog_depth']:
        session.pop(item, None)

    return redirect(url_for('login'))

@app.route('/')
@app.route('/index/')
@login_required
def index():
    user = session['user']
    system_message_body = session['system_message_body']
    system_message_title = session['system_message_title']
    stat_products_complete_24_hrs = session['stat_products_complete_24_hrs']
    stat_backlog_depth = session['stat_backlog_depth']

    if system_message_title or system_message_body:
        display_system_message = True
    else:
        display_system_message = False

    return render_template('index.html',
                           display_system_message=display_system_message,
                           system_message_body=system_message_body,
                           system_message_title=system_message_title,
                           stat_products_complete_24_hrs=stat_products_complete_24_hrs,
                           stat_backlog_depth=stat_backlog_depth,
                           user=user
                           )

@app.route('/ordering/new/')
@login_required
def new_order():
    user = session['user']
    system_message_body = session['system_message_body']
    system_message_title = session['system_message_title']
    stat_products_complete_24_hrs = session['stat_products_complete_24_hrs']
    stat_backlog_depth = session['stat_backlog_depth']

    form_action = '/ordering/submit/'
    if system_message_title or system_message_body:
        display_system_message = True
    else:
        display_system_message = False
    return render_template('new_order.html',
                           display_system_message=display_system_message,
                           system_message_body=system_message_body,
                           system_message_title=system_message_title,
                           form_action=form_action,
                           stat_products_complete_24_hrs=stat_products_complete_24_hrs,
                           stat_backlog_depth=stat_backlog_depth,
                           user=user
                           )


@app.route('/ordering/submit/', methods=['POST'])
@login_required
def submit_order():
    user = session['user']
    # form values come in as an ImmutableMultiDict
    data = request.form.to_dict()

    # grab sceneids from the file in input_product_list field
    _ipl_str = request.files.get('input_product_list').read()
    _splitter = "\n" if "\n" in _ipl_str else "\r"
    _ipl = _ipl_str.split(_splitter)

    # use available-products to convert our list of sceneids into
    # the format required for new orders
    ap_url = api_base_url + "/api/v0/available-products"
    ap_data = {'inputs': _ipl}
    ap_resp = requests.post(ap_url, json=ap_data, auth=(user.username, user.wurd))
    scene_dict_all_prods = ap_resp.json()

    # create a list of requested products
    product_list = []
    for key in data.keys():
        if key in conversions['products'].keys():
            product_list.append(conversions['products'][key])
            # now that we have the product list, lets remove
            # this key from the form inputs
            data.pop(key)

    # pop 'image_extents' if present.
    # the image extents parameters also come in under
    # this key in the form, and this causes a conflict
    # with the 'image_extents' used to enable modifying
    # image extents in the deep_update function
    clk = ['image_extents', 'projection', 'resize']
    for k in clk:
        if k in data.keys():
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
        val = is_num(v)
        if "|" not in k:
            tdict = {k: val}
        else:
            key_list = k.split("|")
            if len(key_list) == 3:
                tdict = {key_list[0]: {key_list[1]: {key_list[2]: val}}}
            else:
                tdict = {key_list[0]: {key_list[1]: val}}

        # deep_update updates the dictionary
        deep_update(out_dict, tdict)

    # the response from available-products returns... all possible products
    # pop the 'outputs' key, add 'products' key with values indicated
    # by user
    for key in scene_dict_all_prods.keys():
            if key != 'not_implemented':
                scene_dict_all_prods[key]['products'] = product_list
                scene_dict_all_prods[key].pop('outputs')

    # combine order options with product lists
    out_dict.update(scene_dict_all_prods)

    # keys to clean up
    cleankeys = ['not_implemented', 'target_projection']
    for item in cleankeys:
        if item in out_dict.keys():
            out_dict.pop(item)

    url = api_base_url + "/api/v0/order"
    response = requests.post(url, json=out_dict, auth=(user.username, user.wurd))
    response_data = response.json()

    # hack till we settle on msg or message
    if 'message' in response_data.keys():
        response_data['msg'] = response_data['message']

    if response.status_code == 200:
        flash("Order submitted successfully! Your OrderId is {}".format(response_data))
        return redirect(url_for('index'))
    else:
        flash("There was an issue submitting your order. {}".format(response_data["msg"]))
        return redirect(url_for('new_order'))

@app.route('/ordering/status/')
@app.route('/ordering/status/<email>/')
@login_required
def list_orders(email=None):
    user = session['user']
    url = api_base_url + "/api/v0/list-orders-ext"
    if email:
        url += "/{0}".format(email)
    json = {'status': ['complete', 'ordered']}
    response = requests.get(url, json=json, auth=(user.username, user.wurd))
    res_data = response.json()
    return render_template('list_orders.html', user=user, order_list=res_data)

@app.route('/ordering/order-status/<orderid>/')
@login_required
def view_order(orderid):
    user = session['user']

    order_dict_url = api_base_url + "/api/v0/order/{}".format(orderid)
    order_dict = requests.get(order_dict_url, auth=(user.username, user.wurd)).json()

    scenes_url = api_base_url + "/api/v0/item-status/{}".format(orderid)
    scenes_resp = requests.get(scenes_url, auth=(user.username, user.wurd)).json()
    scenes = scenes_resp['orderid'][orderid]

    complete = ['complete', 'unavailable']
    open = ['oncache', 'queued', 'processing', 'error', 'submitted']
    waiting = ['retry', 'onorder']
    statuses = {'complete': complete, 'open': open, 'waiting': waiting}

    product_counts = {}
    for status in statuses:
        product_counts[status] = len([s for s in scenes if s['status'] in statuses[status]])
    product_counts['total'] = len(scenes)

    # get away from unicode
    joptions = json.dumps(order_dict['product_opts'])

    # sensor/products
    options_by_sensor = {}
    for key in order_dict['product_opts']:
        if isinstance(order_dict['product_opts'][key], dict) and 'products' in order_dict['product_opts'][key].keys():
            options_by_sensor[key] = order_dict['product_opts'][key]['products']

    options_list = []
    for sensor in options_by_sensor:
        options_list.append(" {0}: {1} ,".format(sensor, ", ".join(options_by_sensor[sensor])))

    options_str = " ".join(options_list)

    return render_template('view_order.html', order=order_dict, scenes=scenes, prod_str=options_str,
                           product_counts=product_counts, user=user, product_opts=joptions)

@app.route('/reports/')
@login_required
def list_reports():
    user = session['user']
    req_url = api_base_url + "/api/v0/reports/"
    response = requests.get(req_url, auth=(user.username, user.wurd))
    res_data = response.json()
    return render_template('list_reports.html', reports=res_data, user=user)

@app.route('/reports/<name>/')
@login_required
def show_report(name):
    user = session['user']
    req_url = api_base_url + "/api/v0/reports/{0}/".format(name)
    response = requests.get(req_url, auth=(user.username, user.wurd))
    res_data = eval(response.json())

    return render_template('report.html', report_name=name, report=res_data, user=user)

@app.route('/console', methods=['GET'])
@login_required
def console():
    user = session['user']
    req_url = api_base_url + "/api/v0/statistics/all"
    response = requests.get(req_url, auth=(user.username, user.wurd))
    data = response.json()
    stats = {'Open Orders': data['stat_open_orders'],
             'Products Complete 24hrs': data['stat_products_complete_24_hrs'],
             'Waiting Users': data['stat_waiting_users'],
             'Backlog Depth': data['stat_backlog_depth']}
    return render_template('console.html', user=user, stats=stats,
                           stat_products_complete_24_hrs=session['stat_products_complete_24_hrs'],
                           stat_backlog_depth=session['stat_backlog_depth'])

@app.route('/console/statusmsg', methods=['GET', 'POST'])
@login_required
def statusmsg():
    user = session['user']
    if request.method == 'POST':
        req_url = api_base_url + '/api/v0/system-status-update'
        dsm = 'False'
        if 'display_system_message' in request.form.keys():
            dsm = 'True'
        api_args = {'system_message_title': request.form['system_message_title'],
                    'system_message_body': request.form['system_message_body'],
                    'display_system_message': dsm}
        response = requests.post(req_url,
                                 data=json.dumps(api_args),
                                 auth=(user.username, user.wurd))
        if response.status_code == 200:
            flash('update successful')
        else:
            flash('update failed')
        return redirect(url_for('statusmsg'))
    else:
        status_response = requests.get(api_base_url + '/api/v0/system-status',
                                       auth=(user.username, user.wurd))
        sys_msg_resp = status_response.json()
        session['system_message_body'] = sys_msg_resp['system_message_body']
        session['system_message_title'] = sys_msg_resp['system_message_title']
        session['display_system_message'] = sys_msg_resp['display_system_message']
        return render_template('statusmsg.html',
                               user=user,
                               display_system_message=session['display_system_message'],
                               system_message_title=session['system_message_title'],
                               system_message_body=session['system_message_body'])

@app.route('/console/config', methods=['GET'])
@login_required
def console_config():
    user = session['user']
    req_url = api_base_url + "/api/v0/system/config"
    response = requests.get(req_url, auth=(user.username, user.wurd))
    config_data = response.json()
    return render_template('config.html',
                           user=user,
                           config_data=config_data,
                           stat_products_complete_24_hrs=session['stat_products_complete_24_hrs'],
                           stat_backlog_depth=session['stat_backlog_depth'])

if __name__ == '__main__':

    app.run(debug=True, use_evalex=False, host='0.0.0.0', port=8889)
