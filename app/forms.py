from flask_wtf import Form
from wtforms import TextField, PasswordField, SubmitField,\
    TextAreaField, SelectField, BooleanField
from wtforms.validators import InputRequired, Length


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
    subreddit = TextField('Choose a Subreddit:', validators=[InputRequired()])
    description = TextAreaField(
        'Why do you want to rate this? (optional)',
        validators=[Length(
            max=600,
            message="Description cannot be longer than 600 characters"
        )]
    )
    category = SelectField('Category:', coerce=int)
    test_mode = BooleanField('Post to reddit?')
    submit = SubmitField()


# frontend thread edit form
class EditThreadForm(Form):
    category = SelectField('Category:', coerce=int)
    submit = SubmitField()
