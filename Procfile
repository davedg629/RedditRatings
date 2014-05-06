web: gunicorn run-heroku:app
init: python db_create.py
crawl: python manage.py crawl --silent=false --label=comments
crawl_silent: python manage.py crawl --silent=true --label=comments
crawl_silent_old: python manage.py crawl --silent=true --label=review
db_migrate: python manage.py db migrate
db_upgrade: python manage.py db upgrade
