from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bootstrap import Bootstrap
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
import praw

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

bootstrap = Bootstrap(app)

r = praw.Reddit(user_agent=app.config['REDDIT_USER_AGENT'])
r.set_oauth_app_info(
    app.config['REDDIT_APP_ID'],
    app.config['REDDIT_APP_SECRET'],
    app.config['OAUTH_REDIRECT_URI']
)

# import Crawl command
from spider import Crawl

manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command('crawl', Crawl)

from app import models, views, admin_views
from admin_views import admin

admin.init_app(app)
