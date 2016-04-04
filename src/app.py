from flask import Flask, request, flash, session, redirect, render_template, url_for
# OrderedDict and datetime used by reports, leave
from collections import OrderedDict
import datetime
from datetime import timedelta
from flask.ext.session import Session
from functools import wraps
from user import User
import requests
import json

app = Flask(__name__)
app.config.from_envvar('ESPAWEB_SETTINGS', silent=False)
app.secret_key = '@ijn@@d)h@8f8avh+h=lzed2gy=hp2w+6+nbgl2sdyh$!x!%3+'
app.config['SESSION_TYPE'] = 'memcached'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

Session(app)
api_base_url = "http://{0}:{1}".format(app.config['APIHOST'], app.config['APIPORT'])

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
    if request.method == 'POST':
        auth_url = api_base_url + "/api/v0/user"
        response = requests.get(auth_url, auth=(request.form['username'], request.form['password']))
        resp_json = json.loads(response._content)
        resp_json['wurd'] = request.form['password']
        user = User(**resp_json)
        if response.status_code == 200:
            session['logged_in'] = True
            session['user'] = user

            status_response = requests.get(api_base_url + '/api/v0/system-status',
                                           auth=(user.username, user.wurd))._content
            sys_msg_resp = json.loads(status_response)
            session['system_message_body'] = sys_msg_resp['system_message_body']
            session['system_message_title'] = sys_msg_resp['system_message_title']
            session['display_system_message'] = sys_msg_resp['display_system_message']
            session['stat_products_complete_24_hrs'] = requests.get(api_base_url+'/api/v0/statistics/stat_products_complete_24_hrs',
                                                                    auth=(user.username, user.wurd))._content
            session['stat_backlog_depth'] = requests.get(api_base_url + '/api/v0/statistics/stat_backlog_depth',
                                              auth=(user.username, user.wurd))._content
            flash('You were logged in')
            return redirect(url_for('index'))
        else:
            error = resp_json['msg']
    return render_template('login.html', error=error, user=user)

@app.route('/logout')
def logout():
    for item in ['logged_in', 'user', 'system_message_body', 'system_message_title',
                 'stat_products_complete_24_hrs', 'stat_backlog_depth']:
        session.pop(item, None)

    flash('You were logged out')
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

    form_action = api_base_url + '/api/v0/order'
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

@app.route('/ordering/status/')
@app.route('/ordering/status/<email>')
@login_required
def list_orders(email=None):
    user = session['user']
    url = api_base_url + "/api/v0/list-orders-ext"
    if email:
        url += "/{0}".format(email)
    response = requests.get(url, auth=(user.username, user.wurd))._content
    res_data = json.loads(response)
    print "****", res_data
    return render_template('list_orders.html', user=user, order_list=res_data)

@app.route('/ordering/status/orderid')
@login_required
def view_order():
    user = session['user']
    return render_template('view_order.html', user=user)

@app.route('/reports/')
@login_required
def list_reports():
    req_url = api_base_url + "/api/v0/reports/"
    response = requests.get(req_url)
    res_data = json.loads(response._content)
    user = session['user']
    return render_template('list_orders.html', reports=res_data, user=user)

@app.route('/reports/<name>/')
@login_required
def show_report(name):
    req_url = api_base_url + "/api/v0/reports/{0}/".format(name)
    response = requests.get(req_url)
    res_data = eval(json.loads(response._content))
    user = session['user']
    return render_template('report.html', report_name=name, report=res_data, user=user)

@app.route('/console', methods=['GET', 'POST'])
@login_required
def console():
    user = session['user']
    if request.method == 'POST':
        req_url = api_base_url + '/api/v0/system-status-update'
        dsm = 'false'
        if 'display_system_message' in request.form.keys():
            dsm = 'true'
        api_args = {'system_message_title': request.form['system_message_title'],
                    'system_message_body': request.form['system_message_body'],
                    'display_system_message': dsm}
        requests.post(req_url, data=json.dumps(api_args), auth=(user.username, user.wurd))

        return redirect(url_for('console'))
    else:
        status_response = requests.get(api_base_url + '/api/v0/system-status',
                                       auth=(user.username, user.wurd))._content
        sys_msg_resp = json.loads(status_response)
        session['system_message_body'] = sys_msg_resp['system_message_body']
        session['system_message_title'] = sys_msg_resp['system_message_title']
        return render_template('console.html',
                               user=user,
                               display_system_message=session['display_system_message'],
                               system_message_title=session['system_message_title'],
                               system_message_body=session['system_message_body'])




if __name__ == '__main__':

    app.run(debug=True, use_evalex=False, host='localhost', port=8889)
