# Importing required modules
from flask import Flask, render_template, request, redirect, url_for, session
import pymysql.cursors
import re

# Creating a Flask web application
app = Flask(__name__)

# Setting a secret key to use sessions
app.secret_key = 'your secret key'

# Configuring the MySQL database details
app.config['MYSQL_HOST'] = 'ap-south.connect.psdb.cloud'
app.config['MYSQL_USER'] = 'cc368utl7dt898dkdz23'
app.config['MYSQL_PASSWORD'] = 'pscale_pw_rHmdaRZZR219HzQ8IFSutYoOqt5HrlUXdn7SX9go8oC'
app.config['MYSQL_DB'] = 'govnotify'

# Creating a MySQL connection object using the above details
mysql = pymysql.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    db=app.config['MYSQL_DB'],
    ssl = {'ssl_ca':'/etc/ssl/cert.pem'},
    cursorclass=pymysql.cursors.DictCursor
)

# Login route to allow users to login to the web application
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''  # Initializing an empty message variable
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Retrieving username and password from the login form
        username = request.form['username']
        password = request.form['password']
        with mysql.cursor() as cursor:
            # Retrieving account details from the database if the username and password match
            cursor.execute('SELECT * FROM log WHERE username = %s AND password = %s', (username, password))
            account = cursor.fetchone()
            if account:  # If the account exists
                # Creating session variables to track the user's login status
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                msg = 'Logged in successfully!'
                return redirect(url_for('home'))  # Redirecting to the index page with a success message
            else:  # If the account does not exist
                msg = 'Incorrect username / password!'
    return render_template('pages-login.html', msg=msg)  # Rendering the login page with the message variable

# Logout route to allow users to log out of the web application
@app.route('/logout')
def logout():
    # Removing session variables to log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))  # Redirecting to the login page after logging out

# Register route to allow users to register for the web application
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''  # Initializing an empty message variable
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Retrieving username, password, and email from the registration form
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        with mysql.cursor() as cursor:
            # Retrieving account details from the database if an account with the same username exists
            cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
            account = cursor.fetchone()
            if account:  # If an account with the same username exists
                msg = 'Account already exists!'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):  # If email is invalid
                msg = 'Invalid email address!'
            elif not re.match(r'[A-Za-z0-9]+', username):  # If username contains invalid characters
                msg = 'Username must contain only characters and numbers!'
            elif not username or not password or not email:  # If any of the fields are empty
                msg = 'Please fill out the form!'
            else:
                cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email))
                mysql.commit()
                msg = 'You have successfully registered!'
    elif request.method == 'POST':  # If request method is POST but fields are empty
        msg = 'Please fill out the form!'
    return render_template('pages-register.html', msg=msg)  # Rendering the registration page with appropriate message.



@app.route('/home')
def home():

  with mysql.cursor() as cursor:
    cursor.execute("select * from sample")
    items = cursor.fetchall()
    return render_template('index.html',items=items)





if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)

