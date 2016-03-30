from flask import Flask
from flask import request
from flask import render_template
from flask import url_for

import requests
import json

from collections import OrderedDict
import datetime

app = Flask(__name__)
app.config.from_envvar('ESPAWEB_SETTINGS', silent=False)

api_base_url = "http://{0}:{1}".format(app.config['APIHOST'], app.config['APIPORT'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))

@app.route('/')
@app.route('/index/')
def index():
    bar = "heres a string"
    response = requests.get(api_base_url + '/api/v0/system-status')._content
    sys_msg_resp = json.loads(response)
    system_message_body = sys_msg_resp['system_message_body']
    system_message_title = sys_msg_resp['system_message_title']
    if system_message_title or system_message_body:
        display_system_message = True
    else:
        display_system_message = False
    print "****", display_system_message
    return render_template('index.html', bar=bar,
                           display_system_message=display_system_message,
                           system_message_body=system_message_body,
                           system_message_title=system_message_title
                           )

@app.route('/ordering/new/')
def new_order():
    return render_template('new_order.html')

@app.route('/ordering/status/')
@app.route('/ordering/status/emailaddr')
def list_orders():
    return render_template('list_orders.html')

@app.route('/ordering/status/orderid')
def view_order():
    return render_template('view_order.html')

@app.route('/reports/')
def list_reports():
    req_url = api_base_url + "/api/v0/reports/"
    response = requests.get(req_url)
    res_data = json.loads(response._content)
    return render_template('list_orders.html', reports=res_data)

@app.route('/reports/<name>/')
def show_report(name):
    req_url = api_base_url + "/api/v0/reports/{0}/".format(name)
    response = requests.get(req_url)
    res_data = eval(json.loads(response._content))
    return render_template('report.html', report_name=name, report=res_data)


if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8889)
