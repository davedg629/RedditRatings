from flask_wtf import Form
from wtforms import TextField, PasswordField, SubmitField,\
    TextAreaField, SelectField, BooleanField
from wtforms.validators import InputRequired, Length, NoneOf


class LoginForm(Form):
    username = TextField('Username:', validators=[InputRequired()])
    password = PasswordField('Password:', validators=[InputRequired()])
    submit = SubmitField()


# frontend thread creation form
class ThreadForm(Form):
    title = TextField(
        'What are we rating?',
        validators=[InputRequired()]
    )
    reddit_title = TextField(
        'Enter a title for your reddit post:',
        validators=[
            InputRequired(),
            Length(
                max=300,
                message="Title cannot be longer than 300 characters"
            )
        ]
    )
    subreddit = TextField('Choose a Subreddit:', validators=[InputRequired()])
    description = TextAreaField(
        'Why do you want to rate this?',
        validators=[
            InputRequired(),
            Length(
                max=600,
                message="Description cannot be longer than 600 characters"
            )
        ]
    )
    category = SelectField(
        'Choose a Category:',
        validators=[NoneOf([0], message="This field is required")],
        coerce=int
    )
    test_mode = BooleanField('Don\'t post to reddit?')
    submit = SubmitField()


# frontend thread edit form
class EditThreadForm(Form):
    category = SelectField('Category:', coerce=int)
    submit = SubmitField()


# close thread form
class CloseThreadForm(Form):
    submit = SubmitField('Yes')
