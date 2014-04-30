from flask_wtf import Form
from wtforms import TextField, PasswordField, SubmitField,\
    TextAreaField, SelectField, BooleanField
from wtforms.validators import InputRequired


class LoginForm(Form):
    username = TextField('Username:', validators=[InputRequired()])
    password = PasswordField('Password:', validators=[InputRequired()])
    submit = SubmitField()


# frontend thread creation form
class ThreadForm(Form):
    title = TextField(
        'What do you want to rate?',
        validators=[InputRequired()]
    )
    subreddit = TextField('Subreddit:', validators=[InputRequired()])
    description = TextAreaField('Optional Description:')
    category = SelectField('Category:', coerce=int)
    test_mode = BooleanField('Post to reddit?')
    submit = SubmitField()
