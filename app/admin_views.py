from app import db, admin, models
from flask.ext.admin.contrib.sqla import ModelView


class CategoryView(ModelView):
    form_excluded_columns = ['community_reviews', ]


class RoleView(ModelView):
    form_excluded_columns = ['users', ]


class UserView(ModelView):
    form_excluded_columns = ['community_reviews', 'user_reviews', ]


class GroupView(ModelView):
    form_excluded_columns = ['community_reviews', ]


class CommunityReviewView(ModelView):
    form_excluded_columns = ['user_reviews', 'last_crawl', ]

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
admin.add_view(ModelView(
    models.UserReview,
    db.session,
    name='User Reviews'
))
