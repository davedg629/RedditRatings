from app import db, admin, models
from flask import session, redirect, url_for
from flask.ext.admin import AdminIndexView, expose
from flask.ext.admin.contrib.sqla import ModelView
from wtforms.validators import InputRequired
from forms import unique_slug


class AdminIndexView(AdminIndexView):

    @expose('/')
    def index(self):
        if not 'logged_in' in session:
            return redirect(url_for('login'))


class AuthMixin(object):
    def is_accessible(self):
        return 'logged_in' in session

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('login'))


class AdminModelView(AuthMixin, ModelView):
    pass


class CategoryView(AdminModelView):
    form_excluded_columns = ['community_reviews', ]


class RoleView(AdminModelView):
    form_excluded_columns = ['users', ]


class UserView(AdminModelView):
    form_excluded_columns = ['community_reviews', 'user_reviews', ]


class GroupView(AdminModelView):
    form_excluded_columns = ['community_reviews', ]


class CommunityReviewView(AdminModelView):
    form_excluded_columns = ['user_reviews', 'slug', 'last_crawl', ]
    form_args = dict(
        title=dict(validators=[InputRequired(), unique_slug])
    )

# add admin views
admin.add_view(CategoryView(
    models.Category,
    db.session,
    name='Categories'
))
admin.add_view(RoleView(
    models.Role,
    db.session,
    name='Roles'
))
admin.add_view(UserView(
    models.User,
    db.session,
    name='Users'
))
admin.add_view(GroupView(models.Group, db.session))
admin.add_view(CommunityReviewView(
    models.CommunityReview,
    db.session,
    name='Community Reviews'
))
admin.add_view(AdminModelView(
    models.UserReview,
    db.session,
    name='User Reviews'
))
