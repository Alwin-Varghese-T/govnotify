# Importing required modules
from flask import Flask, render_template, request, redirect, url_for, session
import pymysql.cursors
import re
import os
from pytz import timezone
from apscheduler.schedulers.background import BackgroundScheduler


#     block python file run sheduler

def run_webscraper_py():

  from webscraper import delete_data, scraper

  delete_data()
  scraper()

# create a scheduler
scheduler = BackgroundScheduler(timezone=timezone('Asia/Kolkata'))
# add job to run run_webscraper_py every 2 hours
scheduler.add_job(run_webscraper_py, 'interval', hours=1)
#starts schedular
scheduler.start()


#    end of sheduler block



# Creating a Flask web application
app = Flask(__name__)

# Setting a secret key to use sessions
app.secret_key = 'os.getenv(your_secret_key)'

# Configuring the MySQL database details
app.config['MYSQL_HOST'] = os.getenv('your_host')
app.config['MYSQL_USER'] = os.getenv('your_username')
app.config['MYSQL_PASSWORD'] = os.getenv('your_password')
app.config['MYSQL_DB'] = os.getenv('your_database')

# Creating a MySQL connection object using the above details
mysql = pymysql.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    db=app.config['MYSQL_DB'],
    ssl = {'ssl_ca':os.getenv('your_ssl_ca')},
    cursorclass=pymysql.cursors.DictCursor
)
#checks if is user in session
@app.route('/')
def check_session():
  if 'username' in session:
    return redirect(url_for('home'))
  else:
    return redirect(url_for('login'))

# Login route to allow users to login to the web application
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
                return redirect(url_for('home'))  # Redirecting to the index page with a success message
            if not account :  # If the account does not exist
                msg = 'Incorrect username / password!'
                return render_template('pages-login.html',msg=msg)
                
    return render_template('pages-login.html')  # Rendering the login page with the message variable

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
            cursor.execute('SELECT * FROM log WHERE username = %s', (username,))
            account = cursor.fetchone()
            if account:  # If an account with the same username exists
                msg = 'Account already exists!'
                return render_template('pages-register.html',msg=msg)
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):  # If email is invalid
                msg = 'Invalid email address!'
                return render_template('pages-register.html',msg=msg)
            elif not re.match(r'[A-Za-z0-9]+', username):  # If username contains invalid characters
                msg = 'Username must contain only characters and numbers!'
                return render_template('pages-register.html',msg=msg)
            elif not username or not password or not email:  # If any of the fields are empty
                msg = 'Please fill out the form!'
                return render_template('pages-register.html',msg=msg)
            else:
                cursor.execute('INSERT INTO log VALUES (NULL, %s, %s, %s)', (username, password, email))
                mysql.commit()
                msg = 'You have successfully registered!'
                return redirect(url_for('login'))
    elif request.method == 'POST':  # If request method is POST but fields are empty
        msg = 'Please fill out the form!'
    return render_template('pages-register.html',msg=msg)  # Rendering the registration page with appropriate message.



@app.route('/home')
def home():
  # check if the user is logged in
  if 'username' in session:
     # if the user is logged in
    with mysql.cursor() as cursor:
      cursor.execute("select * from sample")
      items = cursor.fetchall()
      cursor.execute("select * from latest_news")
      news = cursor.fetchall()
      return render_template('index.html',items=items, news=news)
  else:
      # if the user is not logged in, redirect to the login page
      return redirect(url_for('login'))
  

@app.route('/profile')
def profile():
  return render_template('users-profile.html') 


if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)

