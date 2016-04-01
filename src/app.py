from flask import Flask, request, flash, session, redirect, render_template, url_for
# OrderedDict and datetime used by reports, leave
from collections import OrderedDict
import datetime
from flask.ext.session import Session
from functools import wraps
from user import User
import requests
import json

app = Flask(__name__)
app.config.from_envvar('ESPAWEB_SETTINGS', silent=False)
app.secret_key = '@ijn@@d)h@8f8avh+h=lzed2gy=hp2w+6+nbgl2sdyh$!x!%3+'
app.config['SESSION_TYPE'] = 'memcached'

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
            flash('You were logged in')
            return redirect(url_for('index'))
        else:
            error = resp_json['msg']
    return render_template('login.html', error=error, user=user)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    flash('You were logged out')
    return redirect(url_for('login'))

@app.route('/')
@app.route('/index/')
@login_required
def index():
    user = session['user']
    status_response = requests.get(api_base_url + '/api/v0/system-status', auth=(user.username, user.wurd))._content
    sys_msg_resp = json.loads(status_response)
    system_message_body = sys_msg_resp['system_message_body']
    system_message_title = sys_msg_resp['system_message_title']

    stat_products_complete_24_hrs = requests.get(api_base_url + '/api/v0/statistics/stat_products_complete_24_hrs', auth=(user.username, user.wurd))._content
    stat_backlog_depth = requests.get(api_base_url + '/api/v0/statistics/stat_backlog_depth', auth=(user.username, user.wurd))._content


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
    status_response = requests.get(api_base_url + '/api/v0/system-status')._content
    sys_msg_resp = json.loads(status_response)
    system_message_body = sys_msg_resp['system_message_body']
    system_message_title = sys_msg_resp['system_message_title']
    form_action = api_base_url + '/api/v0/order'
    user = session['user']
    if system_message_title or system_message_body:
        display_system_message = True
    else:
        display_system_message = False
    return render_template('new_order.html',
                           display_system_message=display_system_message,
                           system_message_body=system_message_body,
                           system_message_title=system_message_title,
                           form_action=form_action,
                           user=user
                           )

@app.route('/ordering/status/')
@app.route('/ordering/status/emailaddr')
@login_required
def list_orders():
    user = session['user']
    return render_template('list_orders.html', user=user)

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


if __name__ == '__main__':

    app.run(debug=True, host='localhost', port=8889)
