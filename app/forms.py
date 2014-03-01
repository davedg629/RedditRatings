from app import db
from models import CommunityReview
from flask_wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import InputRequired, ValidationError
from utils import make_slug


def unique_slug(form, field):
    new_slug = make_slug(field.data)
    slug_check = None
    slug_check = db.session.query(CommunityReview)\
        .filter_by(category_id=form.category.data.id)\
        .filter_by(slug=new_slug).first()
    if slug_check:
        raise ValidationError(
            'Title must be unique to the category'
        )


class LoginForm(Form):
    username = TextField('Username:', validators=[InputRequired()])
    password = PasswordField('Password:', validators=[InputRequired()])
