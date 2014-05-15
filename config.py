import os

basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
DEBUG = False

# set to 'heroku' if hosting with heroku
if os.environ.get('ENVIRONMENT') is None:
    ENVIRONMENT = 'dev'
else:
    ENVIRONMENT = os.environ.get('ENVIRONMENT')

# server name
if os.environ.get('SERVER_NAME') is None:
    SERVER_NAME = 'localhost:5000'
else:
    SERVER_NAME = os.environ.get('SERVER_NAME')

# naked server name, set to example.com if ENVIROMENT is set to 'heroku'
if os.environ.get('NAKED_SERVER_NAME') is None:
    NAKED_SERVER_NAME = 'localhost:5000'
else:
    NAKED_SERVER_NAME = os.environ.get('NAKED_SERVER_NAME')

# app name
if os.environ.get('APP_NAME') is None:
    APP_NAME = 'RedditRatings'
else:
    APP_NAME = os.environ.get('APP_NAME')

# flask secret key
if os.environ.get('SECRET_KEY') is None:
    SECRET_KEY = 'a_really_good_secret_key'
else:
    SECRET_KEY = os.environ.get('SECRET_KEY')

# app username and password
if os.environ.get('ADMIN_USERNAME') is None:
    ADMIN_USERNAME = 'admin'
else:
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')

if os.environ.get('ADMIN_PASSWORD') is None:
    ADMIN_PASSWORD = 'admin'
else:
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

# reddit username, password, user agent, app id, and app secret
if os.environ.get('REDDIT_USERNAME') is None:
    REDDIT_USERNAME = 'reddit_username'
else:
    REDDIT_USERNAME = os.environ.get('REDDIT_USERNAME')

if os.environ.get('REDDIT_PASSWORD') is None:
    REDDIT_PASSWORD = 'reddit_password'
else:
    REDDIT_PASSWORD = os.environ.get('REDDIT_PASSWORD')

if os.environ.get('REDDIT_USER_AGENT') is None:
    REDDIT_USER_AGENT = "your app name ver 0.1 by /u/your_user_name, "\
        "https://github.com/davedg629/redditreviewbot"
else:
    REDDIT_USER_AGENT = os.environ.get('REDDIT_USER_AGENT')

if os.environ.get('REDDIT_APP_ID') is None:
    REDDIT_APP_ID = 'reddit_app_id'
else:
    REDDIT_APP_ID = os.environ.get('REDDIT_APP_ID')

if os.environ.get('REDDIT_APP_SECRET') is None:
    REDDIT_APP_SECRET = 'reddit_app_secret'
else:
    REDDIT_APP_SECRET = os.environ.get('REDDIT_APP_SECRET')

if os.environ.get('OAUTH_REDIRECT_URI') is None:
    OAUTH_REDIRECT_URI = 'http://localhost:5000/authorize_callback'
else:
    OAUTH_REDIRECT_URI = os.environ.get('OAUTH_REDIRECT_URI')

if os.environ.get('OAUTH_UNIQUE_KEY') is None:
    OAUTH_UNIQUE_KEY = 'unique_key'
else:
    OAUTH_UNIQUE_KEY = os.environ.get('OAUTH_UNIQUE_KEY')


# SQLALchemy database URI
if os.environ.get('DATABASE_URL') is None:
    DATABASE = 'redditratings.db'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
        os.path.join(basedir, DATABASE) + \
        '?check_same_thread=False'
else:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

# Google Analytics
if os.environ.get('GA_TRACKING_ID') is None:
    GA_TRACKING_ID = 'UA-XXXXXXXX-XX'
else:
    GA_TRACKING_ID = os.environ.get('GA_TRACKING_ID')

if os.environ.get('GA_DEFAULT_URL') is None:
    GA_DEFAULT_URL = 'your-domain.com'
else:
    GA_DEFAULT_URL = os.environ.get('GA_DEFAULT_URL')

# favicon url
if os.environ.get('FAVICON_URL') is None:
    FAVICON_URL = 'url_to_favicon_here'
else:
    FAVICON_URL = os.environ.get('FAVICON_URL')
