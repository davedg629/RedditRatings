from flask_wtf import Form
from wtforms import TextField, PasswordField, SubmitField,\
    TextAreaField, SelectField
from wtforms.validators import InputRequired


class LoginForm(Form):
    username = TextField('Username:', validators=[InputRequired()])
    password = PasswordField('Password:', validators=[InputRequired()])
    submit = SubmitField()


# frontend thread creation form
class ThreadForm(Form):
    title = TextField('What are you rating?', validators=[InputRequired()])
    subreddit = TextField('Subreddit:', validators=[InputRequired()])
    description = TextAreaField('Description (optional):')
    category = SelectField('Category:', coerce=int)
    submit = SubmitField()
