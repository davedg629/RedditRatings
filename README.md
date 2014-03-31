<h1>RedditRatings</h1>

RedditRatings is a Flask app that allows redditors to rate things together.

A working example of the app can be found at http://RedditRatings.com

Ideas, issues, and requests can be discussed at http://reddit.com/r/RedditRatings

You can follow @RedditRatings on Twitter - http://twitter.com/redditratings

<hr />

<h3>Installing the App</h3>

Requirements.txt contains a list of dependencies.

config.py has a number of parameters that can either be hardcoded or set as environment variables. You have to fill them all in or you will likely run into issues.

To initialize the database, run

<pre>python db_create.py</pre>

The app can be served with the Flask development server by running

<pre>python run.py</pre>

There is also a Procfile that can be used for serving the app via gunicorn on Heroku.

<h3>Using the App</h3>

Using the app is a little clunky right now, but will be streamlined as I improve the app.

<ol>
<li>Login at /login/ (use the username/password you set in the config file). This takes you to the "Dashboard".</li>

<li>Go to the "Community Ratings" tab and create a new Community Rating for something. Fill out the form, leaving "Reddit Post ID" and "Reddit Permalink" blank for now.</li>

<li>Go to reddit and create a thread asking users to rate the thing you chose by leaving a comment in the following format:

<pre>
<strong>Rating:</strong> Provide a rating from 1 to 10 here, integers only, required

<strong>Comment:</strong>

Include any comments related to your rating here, encouraged but optional

---

If you want to say something not directly related to your rating, put it below a horizontal rule ('---').

verifyreview

If the text "verifyrating" is included, then a PM will be sent to you when your review is parsed.
</pre>
</li>

<li>After you make your post on reddit, go back to the app Dashboard, edit the Community Rating and fill in the "Reddit Post ID" and "Reddit Permalink" fields.</li>

<li>To pull in the user ratings run the spider script:

<pre>
python manage.py crawl
</pre>

If you are serving the app on Heroku, you can use the following command to run the spider:

<pre>
heroku run crawl
</pre>

The crawl process will post "Success" replies on reddit. You can also run a silent version of the spider script using the following command:

<pre>
heroku run crawl_silent
</pre>

<p>Or setup a cron task to run the spider script automatically.</p>

<p><strong>Warning:</strong> When the crawl script is run, it will check for new comments on each of the Community Ratings that are "Open For Comments". If you don't want to crawl comments for one of the Community Ratings anymore, edit it from the Dashboard and uncheck the "Open For Comments" field.</p>
</li>
</ol>
<hr />

<strong>Note:</strong> This is new to most redditors and not something they will pick up on instantly. So if you decide to give it a try, make sure you explain how this all works in your reddit post.

Also, please let me know if you do give it a try on reddit. You can send me a <a href="http://twitter.com/redditratings" target="_blank">tweet</a> or a <a href="http://www.reddit.com/message/compose/?to=redditratings" target="_blank">reddit PM</a>. I'm always looking for new and better ways to introduce these types of ideas to reddit.

<hr />

<strong>Reddit Review Bot is under the GNU GENERAL PUBLIC LICENSE.</strong>
