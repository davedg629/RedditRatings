from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bootstrap import Bootstrap
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

bootstrap = Bootstrap(app)

# import Crawl command
from spider_new import Crawl

manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command('crawl', Crawl)

from app import models, views, admin_views
from admin_views import admin

admin.init_app(app)
