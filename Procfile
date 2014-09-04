web: gunicorn run-heroku:app
init: python db_create.py
crawl: python manage.py crawl --silent=false --expire=604800
crawl_silent: python manage.py crawl --silent=true --expire=604800
crawl_silent_old: python manage.py crawl --silent=true --expire=604800
db_migrate: python manage.py db migrate
db_upgrade: python manage.py db upgrade
