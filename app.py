# Importing required modules
from flask import Flask, render_template, request, redirect, url_for, session
import pymysql.cursors
import re
import os
from pytz import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from nlp import similarity


#     block python file run sheduler

def run_webscraper_py():

  from webscraper import delete_data, scraper

  delete_data()
  scraper()

# create a scheduler
scheduler = BackgroundScheduler(timezone=timezone('Asia/Kolkata'))
# add job to run run_webscraper_py every 1 hours
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
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Retrieving username and password from the login form
        email = request.form['email']
        password = request.form['password']
        with mysql.cursor() as cursor:
            # Retrieving account details from the database if the username and password match
            cursor.execute('SELECT * FROM account WHERE email = %s AND password = %s', (email, password))
            account = cursor.fetchone()
            if account:  # If the account exists
                # Creating session variables to track the user's login status
                session['loggedin'] = True
                session['email'] = account['email']
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
    session.pop('email', None)
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
        gender = request.form['gender']
        age = request.form['AgeDropdown']
        state = request.form['state']
        category = request.form['category']
        marriage = request.form['marriage']
        
        with mysql.cursor() as cursor:
            # Retrieving account details from the database if an account with the same username exists
            cursor.execute('SELECT * FROM account WHERE email = %s', (email,))
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
                cursor.execute('INSERT INTO account VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (email, username, password, gender, age, state, category, marriage))
                mysql.commit()
                msg = 'You have successfully registered!'
                return redirect(url_for('login'))
    elif request.method == 'POST':  # If request method is POST but fields are empty
        msg = 'Please fill out the form!'
    return render_template('pages-register.html',msg=msg)  # Rendering the registration page with appropriate message.



@app.route('/home')
def home():
  # check if the user is logged in
  if 'email' in session:
     # if the user is logged in
    with mysql.cursor() as cursor:
      email = session['email']
      cursor.execute("select gender, age, state, category , marriage  from account  where email = %s", (email,))
      user_profile = cursor.fetchone()
      cursor.execute("select * from links")
      links = cursor.fetchall()
      items = similarity(user_profile,links)
      cursor.execute("select * from latest_news")
      news = cursor.fetchall()
      return render_template('index.html',items=items, news=news)
  else:
      # if the user is not logged in, redirect to the login page
      return redirect(url_for('login'))
  

@app.route('/profile')
def profile():
  return render_template('users-profile.html') 

@app.route('/admin', methods=['GET', 'POST'])
def admin():
  if request.method == 'POST' and 'name' in request.form and 'link' in request.form and 'description' in request.form:
    name = request.form['name']
    link = request.form['link']
    description = request.form['description']

    with mysql.cursor() as cursor:
      cursor.execute('INSERT INTO links values(%s, %s, %s)', ( name, link, description))
      mysql.commit()
    
  return render_template('admin.html')


if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)

