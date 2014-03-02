from flask_wtf import Form
from wtforms import TextField, PasswordField, SubmitField
from wtforms.validators import InputRequired


class LoginForm(Form):
    username = TextField('Username:', validators=[InputRequired()])
    password = PasswordField('Password:', validators=[InputRequired()])
    submit = SubmitField()
