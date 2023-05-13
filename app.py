# Importing required modules
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from webscraper import scraper
from generate_mail import generate, bulkmail
from dbutils.pooled_db import PooledDB
import pymysql.cursors
import os
import threading

from nlp_cluster import similarity, search_nlp
from nlp_classifier import predict
from datetime import datetime, timedelta
import time

# Creating a Flask web application
app = Flask(__name__)

# global dictionary to store the OTPs
otp_store = {}

# Setting a secret key to use sessions
app.secret_key = 'os.getenv(your_secret_key)'

# Set the default session lifetime to 7 days if user checked the checkbox
app.permanent_session_lifetime = timedelta(days=7)


#it will clear all cache when user logout
@app.after_request
def add_cache_control(response):
  if not session.get('user_id'):
    # If the user is not logged in, set the cache-control header to no-cache
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Expires'] = 0
    response.headers['Pragma'] = 'no-cache'
  return response


#mysql pool connection
pool = PooledDB(creator=pymysql,
                maxconnections=5,
                host=os.getenv('your_host'),
                user=os.getenv('your_username'),
                password=os.getenv('your_password'),
                database=os.getenv('your_database'),
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True,
                ssl={'ssl_ca': os.getenv('your_ssl_ca')})
mysql = pool.connection()


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
    remember = request.form.get('remember')

    with mysql.cursor() as cursor:
      #Retrieving data form admin table
      cursor.execute("select * from admin where username = %s and password = %s",(email,password))
      admin = cursor.fetchone()
      if admin:
        session['loggedin']= True
        session['admin'] =admin['username']
        session.permanent = False
        return redirect(url_for('admin'))
      # Retrieving account details from the database if the username and password match
      cursor.execute(
        'SELECT * FROM accounts WHERE email = %s AND password = %s ',
        (email, password))
      account = cursor.fetchone()
      if account:  # If the account exists
        # Creating session variables to track the user's login status
        session['loggedin'] = True
        session['email'] = account['email']
        session['username'] = account['username']
        #the code below will work only if user checked checkbox
        if remember:
          session.permanent = True
        else:
          session.permanent = False

        return redirect(url_for(
          'home'))  # Redirecting to the index page with a success message
      if not account:  # If the account does not exist
        msg = 'Incorrect username / password!'
        return render_template('pages-login.html', msg=msg)
  return render_template('pages-login.html')  # Rendering the login page with the message variable

#if user forgot his password
@app.route("/forgotpass",methods=['GET', 'POST'])
def forgotpass():
  msg=""
  if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
    email = request.form['email']
    password = request.form['password']
    with mysql.cursor() as cursor:
      cursor.execute('SELECT * FROM accounts WHERE email = %s',(email))
      account = cursor.fetchone()
      if account:
          cursor.execute("UPDATE accounts SET password = %s where email = %s",(password,email))
          registered = True
          abc = "Successfully Changed Password ):"
          return render_template('pages-login.html',registered=registered,abc=abc)
      else:
          msg='Sorry!! Email Is Not In Database :('
          return render_template('forgotpass.html',msg=msg)
  return render_template('forgotpass.html')     
# Logout route to allow users to log out of the web application!
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

    marriage = request.form['marriage']
    seniorty = request.form['seniority']
    belong = request.form['belong']
    diff = request.form['differentlyabled']
    ration = request.form['bpl']
    income = request.form['income']
    
    category = request.form['category']
    
    checkbox_values_list = request.form.getlist('checkboxes')
    if checkbox_values_list:
        checkbox_values_list = list(set(checkbox_values_list))
        checkbox = ",".join(checkbox_values_list)
    else:
        checkbox="All"
    if 'notifications' in request.form:
        notify = request.form['notifications']
    else:
        notify = "No"

    with mysql.cursor() as cursor:
      # Retrieving account details from the database if an account with the same username exists
      cursor.execute('SELECT * FROM accounts WHERE email = %s', (email, ))
      account = cursor.fetchone()
      if account:  # If an account with the same username exists
        msg = 'Account already exists!'
        return render_template('pages-register.html', msg=msg)
      else:
        cursor.execute(
          'INSERT INTO accounts VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
          (username, email, password, gender, age, marriage, seniorty, belong,
           diff, ration, income, category, checkbox, notify))

        registered = True
        abc="Successfully Registered :)"
        return render_template('pages-login.html',registered=registered,abc=abc)
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
    cat_links, other_links = similarity(email)
    with mysql.cursor() as cursor:
      cursor.execute("select * from accounts  where email = %s", (email))
      user = cursor.fetchone()
      one_week_ago = datetime.now() - timedelta(days=7)
      query = f"SELECT * FROM latest_links WHERE created_at >= '{one_week_ago}' ORDER BY created_at DESC"
      cursor.execute(query)
      latest_links = cursor.fetchall()
      news = scraper()
      return render_template('index.html',
                             cat_links=cat_links,
                             other_links=other_links,
                             news=news,
                             user=user,
                             latest_links=latest_links)
  else:
    # if the user is not logged in, redirect to the login page
    return redirect(url_for('login'))


#edit profile


@app.route('/profile', methods=['GET', 'POST'])
def profile():

  if 'email' in session:
    email = session['email']
    with mysql.cursor() as cursor:
      #edit notification status
      form_id = request.form.get('form_id')
      if request.method == 'POST' and form_id == 'notification' :
        if 'notify' in request.form:
            notify = request.form['notify']
        else:
            notify="No"
        cursor.execute("UPDATE accounts SET notify = %s where email = %s",(notify,email))  
      #change password  
      if request.method == 'POST' and form_id == 'change_password':
        newpassword = request.form['password']
        cursor.execute("UPDATE accounts SET password = %s where email = %s",(newpassword,email))
      
      #edit profile
      if request.method == 'POST' and 'username' in request.form:
       
        username = request.form['username']
        gender = request.form['gender']
        age = request.form['AgeDropdown']
        marriage = request.form['marriage']
        seniorty = request.form['seniority']
        belong = request.form['belong']
        diff = request.form['diff']
        ration = request.form['ration']
        income = request.form['income']
        category = request.form['category']

        checkbox_values_list = request.form.getlist('checkboxes')
        if checkbox_values_list:
          checkbox_values_list = list(set(checkbox_values_list))
          checkbox = ",".join(checkbox_values_list)
        else:
          checkbox = "All"
        qurey = "UPDATE accounts SET username= %s, gender = %s, age = %s, marriage = %s, seniorty = %s, belong = %s, diff = %s, ration = %s, income = %s, category = %s, checkbox = %s WHERE email = %s"
        cursor.execute(qurey,
                       (username, gender, age, marriage, seniorty, belong,
                        diff, ration, income, category, checkbox, email))

      cursor.execute("select * from accounts  where email = %s", (email))
      user = cursor.fetchone()
      checklist = user["checkbox"].split(",")

    return render_template('users-profile.html',
                           user=user,
                           checklist=checklist)
  else:
    return redirect(url_for('login'))


@app.route('/admin', methods=['GET', 'POST'])
def admin():
  if 'admin' in session:
    # to get id of button of a ajax request
    button_id = request.form.get('button_id')
    # to check the id and run the prediction function
    if request.method == 'POST' and button_id == 'predict_button':
      data1 = request.form.get('input_data')
      predicted_output = predict(data1)
      return jsonify({'predicted_output': predicted_output})
    # to submit the form to the database
    if request.method == 'POST' and 'name' in request.form and 'link' in request.form and 'description' in request.form and 'category' in request.form:
      sname = request.form['name']
      links = request.form['link']
      descripton = request.form['description']
      keywords = request.form['Keywords'] 
      category = request.form['category']
      cat = category.lower()
      with mysql.cursor() as cursor:
        cursor.execute("select sname from schemes where sname = %s ",(sname))
        check = cursor.fetchall()
        if check:
          msg = "scheme already add"
          return render_template('admin.html',msg=msg)
        else:
          cursor.execute('INSERT INTO schemes values(%s, %s, %s, %s, %s)',
                         (sname, descripton, keywords, links, category))
          cursor.execute(
            "select email from accounts where notify = 'yes' and category = %s",
            (cat))
          mail_address = cursor.fetchall()
          print(mail_address)
          bulkmail(mail_address,sname,descripton)
          cursor.execute('insert into latest_links(title,url,des,category) values(%s,%s,%s,%s)',(sname,links,descripton,category)) 
    return render_template('admin.html')
  else:
    return redirect(url_for('login'))



@app.route('/search', methods=['GET', 'POST'])
def search():
  if 'email' in session:
    if request.method and 'search_element' in request.form:
      search_element = request.form['search_element']
      sh = search_nlp(search_element)
      with mysql.cursor() as cursor:
        email = session['email']
        cursor.execute("select * from accounts  where email = %s", (email))
        user = cursor.fetchone()
        return render_template('search.html', sh=sh, user=user)
    else:
      return redirect(url_for('login'))


@app.route('/image_edit')
def image_edit():
  if 'email' in session:
    email = session['email']
    with mysql.cursor() as cursor:
      cursor.execute("select * from accounts  where email = %s", (email))
      user = cursor.fetchone()

    return render_template('image-edit.html', user=user)
  else:
    return redirect(url_for('login'))


#code for email verification


@app.route('/sampleotp')
def sampleotp():
  return render_template('sample_otp_registeration.html')


@app.route('/generate_otp', methods=['POST'])
def generate_otp():

  email = request.json.get('email')
  otp = generate(email)
  otp_store[email] = otp
  # send email here
  message = f'Your OTP is {otp}'
  print(message)
  return jsonify({'otp': otp})


@app.route('/verify_otp', methods=['POST'])
def verify_otp():
  otp = request.json.get('otp')
  email = request.json.get('email')
  stored_otp = otp_store.get(email)
  print(f'user OTP is {otp}')
  print(f'stored OTP is {stored_otp}')
  if stored_otp and int(stored_otp) == int(otp):
    return jsonify({'isValid': 'True'})
  else:
    return jsonify({'isValid': 'False'})


@app.route('/pdf')
def pdf():
  if 'email' in session:
    email = session['email']
    with mysql.cursor() as cursor:
      cursor.execute("select * from accounts  where email = %s", (email))
      user = cursor.fetchone()

    return render_template('pdf.html', user=user)
  else:
    return redirect(url_for('login'))


#delete the links from latest_links table
def delete_expired_links():
  conn = pool.connection()
  while True: 
    try:
      # delete rows that were created more than a week ago
      one_week_ago = datetime.now() - timedelta(days=3)
      with conn.cursor() as cursor:
        query = f"DELETE FROM latest_links WHERE created_at < '{one_week_ago}'"
        cursor.execute(query)
    except Exception as e:
      # handle any exceptions that may occur
      print(f"Error deleting expired links: {e}")

    # sleep until midnight
    now = datetime.now()
    tomorrow = datetime.combine(now.date() + timedelta(days=1),
                                datetime.min.time())
    time_to_sleep = (tomorrow - now).total_seconds()
    time.sleep(time_to_sleep)
  conn.close()


if __name__ == '__main__':
  # start the deletion thread
  deletion_thread = threading.Thread(target=delete_expired_links)
  deletion_thread.start()
  # run the Flask app
  app.run(host='0.0.0.0', debug=True)



#end









