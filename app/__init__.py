import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

from app import models, views, admin_views
from admin_views import admin

admin.init_app(app)

if not app.debug and os.environ.get('HEROKU') is None:
    import logging

    from logging import Formatter, FileHandler
    from config import basedir

    file_handler = FileHandler(os.path.join(basedir, 'error.log'))
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s '
                  '[in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('app startup')

if os.environ.get('HEROKU') is not None:
    import logging
    stream_handler = logging.StreamHandler()
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('reddit reviews startup')
