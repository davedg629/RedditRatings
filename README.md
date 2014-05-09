<h1>RedditRatings</h1>

RedditRatings is a Flask app that allows redditors to rate things together.

A working example of the app can be found at http://RedditRatings.com

Ideas, issues, and requests can be discussed at http://reddit.com/r/RedditRatings

<hr />

<h3>Installing the App</h3>

Requirements.txt contains a list of dependencies.

config.py has a number of parameters that can either be hardcoded or set as environment variables. You have to fill them all in or you will likely run into issues.

To initialize the database, run

<pre>python db_create.py</pre>

The app can be served with the Flask development server by running

<pre>python run.py</pre>

There is also a Procfile that can be used for serving the app via gunicorn on Heroku.

<h3>How It Works</h3>

See www.redditratings.com/how-it-works/

<hr />

<strong>Reddit Review Bot is under the GNU GENERAL PUBLIC LICENSE.</strong>
