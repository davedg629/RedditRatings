from app import db
from datetime import datetime
from app.utils import make_slug
from sqlalchemy.sql import func


class Category(db.Model):

    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    slug = db.Column(db.String, unique=True, nullable=False)

    community_reviews = db.relationship(
        'CommunityReview',
        backref='category',
        lazy='dynamic'
    )

    def __unicode__(self):
        return self.name


class Role(db.Model):

    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    users = db.relationship(
        'User',
        backref='role',
        lazy='dynamic'
    )

    def __unicode__(self):
        return self.name


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    role_id = db.Column(
        db.Integer,
        db.ForeignKey('roles.id'),
        nullable=False
    )

    community_reviews = db.relationship(
        'CommunityReview',
        backref='user',
        lazy='dynamic'
    )

    user_reviews = db.relationship(
        'UserReview',
        backref='user',
        lazy='dynamic'
    )

    def __unicode__(self):
        return self.username


# create association table for Group/CommunityReview relationship
memberships = db.Table(
    'memberships',
    db.Column(
        'community_review_id',
        db.Integer,
        db.ForeignKey('community_reviews.id')
    ),
    db.Column(
        'group_id',
        db.Integer,
        db.ForeignKey('groups.id')
    )
)


class Group(db.Model):

    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    slug = db.Column(db.String, unique=True, nullable=False)

    def __unicode__(self):
        return self.name


class CommunityReview(db.Model):

    __tablename__ = "community_reviews"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )
    title = db.Column(db.String, nullable=False)

    def get_slug(context):
        return make_slug(context.current_parameters['title'])

    slug = db.Column(
        db.String,
        nullable=False,
        default=get_slug
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey('categories.id'),
        nullable=False
    )
    reddit_id = db.Column(db.String)
    reddit_permalink = db.Column(db.String)
    reddit_score = db.Column(db.Integer, nullable=False, default=1)
    subreddit = db.Column(db.String, nullable=False)
    date_posted = db.Column(
        db.DateTime,
        default=datetime.utcnow(),
        nullable=False
    )
    open_for_comments = db.Column(db.Boolean, default=True, nullable=False)
    last_crawl = db.Column(db.DateTime)

    groups = db.relationship(
        'Group',
        secondary=memberships,
        backref=db.backref('community_reviews', lazy='dynamic'),
        lazy='dynamic')

    user_reviews = db.relationship(
        'UserReview',
        backref='community_review',
        lazy='dynamic'
    )

    def get_avg_rating(self):
        avg_rating = db.session\
            .query(func.avg(UserReview.rating))\
            .filter_by(community_review_id=self.id)
        return "{0:.2f}".format(avg_rating[0][0])

    def get_review_count(self):
        review_count = db.session\
            .query(func.count(UserReview.id))\
            .filter_by(community_review_id=self.id)
        if review_count[0][0] == 1:
            review_count_string = str(review_count[0][0]) + ' rating'
        else:
            review_count_string = str(review_count[0][0]) + ' ratings'
        return review_count_string

    def __unicode__(self):
        return self.title + ' - ' + str(self.category_id)


class UserReview(db.Model):

    __tablename__ = "user_reviews"

    id = db.Column(db.Integer, primary_key=True)
    community_review_id = db.Column(
        db.Integer,
        db.ForeignKey('community_reviews.id'),
        nullable=False
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )
    reddit_id = db.Column(db.String, nullable=False, unique=True)
    date_posted = db.Column(db.DateTime, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String)
    reddit_score = db.Column(db.Integer, nullable=False)
    edited_stamp = db.Column(db.Integer, nullable=False)

    def __unicode__(self):
        return self.reddit_id
