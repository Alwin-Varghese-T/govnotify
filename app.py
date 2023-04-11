
# Importing required modules
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from webscraper import scraper
from generate_mail import generate
import pymysql.cursors
import re
import os

from nlp_cluster import similarity, search_nlp
from nlp_classifier import predict

# Creating a Flask web application
app = Flask(__name__)
# global dictionary to store the OTPs
otp_store = {}

# Setting a secret key to use sessions
app.secret_key = 'os.getenv(your_secret_key)'

# Configuring the MySQL database details
app.config['MYSQL_HOST'] = os.getenv('your_host')
app.config['MYSQL_USER'] = os.getenv('your_username')
app.config['MYSQL_PASSWORD'] = os.getenv('your_password')
app.config['MYSQL_DB'] = os.getenv('your_database')

# Creating a MySQL connection object using the above details
mysql = pymysql.connect(host=app.config['MYSQL_HOST'],
                        user=app.config['MYSQL_USER'],
                        password=app.config['MYSQL_PASSWORD'],
                        db=app.config['MYSQL_DB'],
                        ssl={'ssl_ca': os.getenv('your_ssl_ca')},
                        cursorclass=pymysql.cursors.DictCursor)





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
      cursor.execute(
        'SELECT * FROM account WHERE email = %s AND password = %s ',
        (email, password))
      account = cursor.fetchone()
      if account:  # If the account exists
        # Creating session variables to track the user's login status
        session['loggedin'] = True
        session['email'] = account['email']
        session['username'] = account['username']
        return redirect(url_for(
          'home'))  # Redirecting to the index page with a success message
      if not account:  # If the account does not exist
        msg = 'Incorrect username / password!'
        return render_template('pages-login.html', msg=msg)

  return render_template(
    'pages-login.html')  # Rendering the login page with the message variable


# Logout route to allow users to log out of the web application
@app.route('/logout')
def logout():
  # Removing session variables to log the user out
  session.pop('loggedin', None)
  session.pop('email', None)
  session.pop('username', None)
  return redirect(
    url_for('login'))  # Redirecting to the login page after logging out


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
      cursor.execute('SELECT * FROM account WHERE email = %s', (email, ))
      account = cursor.fetchone()
      if account:  # If an account with the same username exists
        msg = 'Account already exists!'
        return render_template('pages-register.html', msg=msg)
      elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):  # If email is invalid
        msg = 'Invalid email address!'
        return render_template('pages-register.html', msg=msg)
      elif not re.match(r'[A-Za-z0-9]+',
                        username):  # If username contains invalid characters
        msg = 'Username must contain only characters and numbers!'
        return render_template('pages-register.html', msg=msg)
      elif not username or not password or not email:  # If any of the fields are empty
        msg = 'Please fill out the form!'
        return render_template('pages-register.html', msg=msg)
      else:
        cursor.execute(
          'INSERT INTO account VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
          (email, username, password, gender, age, state, category, marriage))
        mysql.commit()
        msg = 'You have successfully registered!'
        return redirect(url_for('login'))
  elif request.method == 'POST':  # If request method is POST but fields are empty
    msg = 'Please fill out the form!'
  return render_template(
    'pages-register.html',
    msg=msg)  # Rendering the registration page with appropriate message.


@app.route('/home')
def home():
  # check if the user is logged in
  if 'email' in session:
    email = session['email']
    # if the user is logged in
    items = similarity(email)
    with mysql.cursor() as cursor:
      cursor.execute("select * from account  where email = %s",(email))
      user=cursor.fetchone()
      news = scraper()
      return render_template('index.html',items=items,news=news,user=user)
  else:
    # if the user is not logged in, redirect to the login page
    return redirect(url_for('login'))


@app.route('/profile')
def profile():
  if 'email' in session:
    email = session['email']
    with mysql.cursor() as cursor:
      cursor.execute("select * from account  where email = %s",(email))
      user=cursor.fetchone()
    
    return render_template('users-profile.html',user=user)
  else:
    return redirect(url_for('login'))


@app.route('/admin', methods=['GET', 'POST'])
def admin():
  # to get id of button of a ajax request
  button_id = request.form.get('button_id')
  # to check the id and run the prediction function
  if request.method == 'POST' and button_id == 'predict_button':
    data1 = request.form.get('input_data')
    predicted_output = predict(data1)
    return jsonify({'predicted_output': predicted_output})
  # to submit the form to the database
  if request.method == 'POST' and 'name' in request.form and 'link' in request.form and 'description' in request.form and 'category'in request.form :
    sname = request.form['name']
    links = request.form['link']
    descripton = request.form['description']
    keywords = request.form['Keywords']
    category = request.form['category']
    
    with mysql.cursor() as cursor:
      cursor.execute('INSERT INTO schemes values(%s, %s, %s, %s, %s)',
                     (sname, descripton, keywords, links, category))
      mysql.commit()

  return render_template('admin.html')


@app.route('/priority', methods=['GET', 'POST'])
def priority():

  if request.method == 'POST' and 'genderpriority' in request.form and 'AgeDropdown' in request.form and 'state' in request.form and 'caste' in request.form and 'marriage' in request.form:

    gender = request.form['genderpriority']
    age = request.form['AgeDropdown']
    state = request.form['state']
    caste = request.form['caste']
    marriage = request.form['marriage']

    with mysql.cursor() as cursor:
      id = 'admin'
      cursor.execute(
        'UPDATE priority SET gender = %s, age = %s, state = %s, category = %s, marriage = %s WHERE id = %s ',
        (gender, age, state, caste, marriage, id))
      mysql.commit()

  return render_template('user-priority.html')


@app.route('/home/search', methods=['GET', 'POST'])
def search():
  if 'email' in session:
    if request.method and 'search_element' in request.form:
      search_element = request.form['search_element']
      sh = search_nlp(search_element)
      return render_template('search.html',sh=sh)
    else:
      return redirect(url_for('login'))


@app.route('/image_edit')
def image_edit():
  if 'email' in session:
    email = session['email']
    with mysql.cursor() as cursor:
      cursor.execute("select * from account  where email = %s",(email))
      user=cursor.fetchone()
    
    return render_template('image-edit.html',user=user)
  else:
    return redirect(url_for('login'))




#code for email verification





@app.route('/sampleotp')
def sampleotp():
  return render_template('sample_otp_registeration.html')

  
@app.route('/send_otp', methods=['POST'])
def send_otp():
    email = request.form['email']
    otp = generate(email)
    otp_store[email] = otp
    # send email here
    message = f'Your OTP is {otp}'
    print(message)
    return jsonify({'status': 'success', 'message': 'OTP sent successfully'})

@app.route('/verify', methods=['POST'])
def verify_otp():
    email = request.form['email']
    user_otp = request.form['otp']
    stored_otp = otp_store.get(email)
    print(f'user OTP is {user_otp}')
    print(f'stored OTP is {stored_otp}')
    if stored_otp and int(stored_otp) == int(user_otp):
        return jsonify({'status': 'success', 'message': 'OTP verified successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid OTP'})



if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)


