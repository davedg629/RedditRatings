web: gunicorn run-heroku:app
init: python db_create.py
crawl: python manage.py crawl
crawl_silent: python manage.py crawl --silent=true
crawl_silent_old: python app/spider_silent_old.py
db_migrate: python manage.py db migrate
db_upgrade: python manage.py db upgrade
