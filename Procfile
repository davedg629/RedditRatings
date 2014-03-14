web: gunicorn run-heroku:app
init: python db_create.py
crawl: python app/spider.py
crawl_silent: python app/spider_silent.py
crawl_silent_old: python app/spider_silent_old.py
db_migrate: python manage.py db migrate
db_upgrade: python manage.py db upgrade
