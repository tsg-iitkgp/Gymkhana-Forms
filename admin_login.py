from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField

class AdminLogin(FlaskForm):
    username = StringField('Admin Username')
    password = PasswordField('Password')
    submit = SubmitField('Submit')