<h1>Reddit Review Bot</h1>

Reddit Review Bot is a Flask app that allows redditors to create Community Reviews of anything by commenting on a reddit thread using a specific review format.

A working example of the app can be found at http://RedditReview.com

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

<li>Find the "Create Community Review" link and click on it. Fill out the form, leaving "Reddit Post ID" and "Reddit Permalink" blank for now.</li>

<li>Go to reddit and create a thread asking users to review the game you chose by leaving a comment in the following format:

<pre>
<strong>Rating:</strong> [Provide a rating from 1 to 10 here, integers only, required]

<strong>Review:</strong>

[Write your review of the game here, keep it short &amp; focus on your experience, optional]

---

If you want to say something in your comment that is not part of your review,
use a horizontal rule ("---") to divide your review from your non-review comments.
</pre>
</li>

<li>After you make your post on reddit, go back to the app Dashboard, edit the Community Review and fill in the "Reddit Post ID" and "Reddit Permalink" fields.</li>

<li>To pull in the user reviews run the spider script:

<pre>
python app/spider.py
</pre>

If you are serving the app on Heroku, you can use the following command to run the spider:

<pre>
heroku run crawl
</pre>

The crawl process will post "Success" replies on reddit. You can also run a silent version of the spider script using the following command:

<pre>
heroku run silent_crawl
</pre>

<p>Or setup a cron task to run the spider script automatically.</p>

<p><strong>Warning:</strong> When the crawl script is run, it will check for new comments on each of the Community Reviews that are "Open For Comments". If you don't want to crawl comments for one of the Community Reviews anymore, edit it from the Dashboard and uncheck the "Open For Comments" field.</p>
</li>
</ol>
<hr />

<strong>Note:</strong> This is new to most redditors and not something they will pick up on instantly. So if you decide to give it a try, make sure you explain how this all works in your reddit post.

Also, please let me know if you do give it a try on reddit. You can send me a <a href="http://twitter.com/daviddigiovanni" target="_blank">tweet</a> or an <a href="http://groupsrc.com/contact" target="_blank">email</a>. I'm always looking for new and better ways to introduce these types of ideas to reddit.

<hr />

<strong>Reddit Review Bot is under the GNU GENERAL PUBLIC LICENSE.</strong>
