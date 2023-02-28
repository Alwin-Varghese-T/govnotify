from flask import Flask, render_template
from database import load_links

app = Flask(__name__)

#showing data from db

@app.route('/')
@app.route('/pages-login.html')
def login():
  return render_template('pages-login.html')


@app.route('/index.html')
def home():
  items = load_links()
  return render_template('index.html', items=items)


@app.route('/users-profile.html')
def user():
  return render_template('users-profile.html')


@app.route('/pages-register.html')
def register():
  return render_template('pages-register.html')


if __name__ == '__main__':
  app.run(host='0.0.0.0', debug=True)