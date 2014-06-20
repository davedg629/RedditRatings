from app import db, login_manager
from datetime import datetime
from app.utils import make_slug
from sqlalchemy.sql import func
from flask.ext.login import UserMixin


class Category(db.Model):

    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    slug = db.Column(db.String, unique=True, nullable=False)

    threads = db.relationship(
        'Thread',
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


class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    role_id = db.Column(
        db.Integer,
        db.ForeignKey('roles.id'),
        nullable=False
    )
    refresh_token = db.Column(db.String)

    threads = db.relationship(
        'Thread',
        backref='user',
        lazy='dynamic'
    )

    comments = db.relationship(
        'Comment',
        backref='user',
        lazy='dynamic'
    )

    def get_avg_rating(self):
        avg_rating = db.session\
            .query(func.avg(Comment.rating))\
            .filter_by(user_id=self.id)
        if avg_rating[0][0] is None:
            avg = 0
        else:
            avg = avg_rating[0][0]
        return "{0:.2f}".format(avg)

    def get_comment_count(self):
        count = db.session\
            .query(func.count(Comment.id))\
            .filter_by(user_id=self.id)
        count_string = str(count[0][0])
        return count_string

    def get_thread_count(self):
        count = db.session\
            .query(func.count(Thread.id))\
            .filter_by(user_id=self.id)
        count_string = str(count[0][0])
        return count_string

    def __unicode__(self):
        return self.username


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# create association table for Tag/Thread relationship
tag_assocs = db.Table(
    'tag_assocs',
    db.Column(
        'thread_id',
        db.Integer,
        db.ForeignKey('threads.id')
    ),
    db.Column(
        'tag_id',
        db.Integer,
        db.ForeignKey('tags.id')
    )
)


class Tag(db.Model):

    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    slug = db.Column(db.String, unique=True, nullable=False)

    def __unicode__(self):
        return self.name


class Thread(db.Model):

    __tablename__ = "threads"

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
    subreddit = db.Column(db.String, nullable=False)
    link_url = db.Column(db.String)
    link_text = db.Column(db.String)
    upvotes = db.Column(db.Integer, nullable=False, default=1)
    downvotes = db.Column(db.Integer, nullable=False, default=0)
    date_posted = db.Column(
        db.DateTime,
        default=datetime.utcnow(),
        nullable=False
    )
    open_for_comments = db.Column(db.Boolean, default=True, nullable=False)
    last_crawl = db.Column(db.DateTime)

    tags = db.relationship(
        'Tag',
        secondary=tag_assocs,
        backref=db.backref('threads', lazy='dynamic'),
        lazy='dynamic')

    comments = db.relationship(
        'Comment',
        backref='thread',
        lazy='dynamic'
    )

    def get_avg_rating(self):
        avg_rating = db.session\
            .query(func.avg(Comment.rating))\
            .filter_by(thread_id=self.id)
        if avg_rating[0][0] is None:
            avg = 0
        else:
            avg = avg_rating[0][0]
        return "{0:.2f}".format(avg)

    def get_comment_count(self):
        count = db.session\
            .query(func.count(Comment.id))\
            .filter_by(thread_id=self.id)
        count_string = str(count[0][0])
        return count_string

    def __unicode__(self):
        return self.title + ' - ' + str(self.category_id)


class Comment(db.Model):

    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(
        db.Integer,
        db.ForeignKey('threads.id'),
        nullable=False
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )
    reddit_id = db.Column(db.String, nullable=False, unique=True)
    date_posted = db.Column(db.DateTime, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    body = db.Column(db.Text)
    upvotes = db.Column(db.Integer, nullable=False)
    downvotes = db.Column(db.Integer, nullable=False)
    edited_stamp = db.Column(db.Integer, nullable=False)

    def __unicode__(self):
        return self.reddit_id
