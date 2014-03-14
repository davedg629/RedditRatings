from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.bootstrap import Bootstrap
from flask.ext.script import Manager

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
manager = Manager(app)

from app import models, views, admin_views
from admin_views import admin

admin.init_app(app)
