from flask import Flask
from flask import request
from flask import g
from flask import render_template
from flask import url_for

app = Flask(__name__)
app.config.from_envvar('ESPAWEB_SETTINGS', silent=False)

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
def index():
    return render_template('index.html')

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

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8889)
