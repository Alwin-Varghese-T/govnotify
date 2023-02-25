from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,EmailField,SubmitField


class RegisterFrom(FlaskForm):
  username = StringField(label='username')
  email_address = EmailField(label='email')
  password1 = PasswordField(label='password1')
  password2 = PasswordField(label='password2')
  submit = SubmitField(label='submit')