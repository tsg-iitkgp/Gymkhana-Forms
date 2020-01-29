from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField

class AdminLogin(FlaskForm):
    username = StringField('Admin usernmae')
    password = PasswordField('Password')
    submit = SubmitField('Submit')