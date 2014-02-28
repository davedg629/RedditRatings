from flask_wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import Required


class LoginForm(Form):
    username = TextField('Username:', validators=[Required()])
    password = PasswordField('Password:', validators=[Required()])
