from app import app, db, r
from flask import flash, redirect, render_template, request, \
    session, url_for, abort, Markup, g
from flask.ext.login import login_user, logout_user, \
    login_required, current_user
from app.forms import LoginForm, ThreadForm, EditThreadForm, \
    CloseThreadForm
from app.models import Category, Tag, Thread, \
    Comment, User
from app.utils import pretty_date, reddit_body, generate_token
from app.decorators import admin_login_required
from datetime import datetime, timedelta
import praw
from app.utils import make_slug
from requests import HTTPError

# redirect to www
if app.config['ENVIRONMENT'] == 'heroku':
    from urlparse import urlparse, urlunparse

    @app.before_request
    def redirect_nonwww():
        """Redirect non-www requests to www."""
        urlparts = urlparse(request.url)
        if urlparts.netloc == app.config['NAKED_SERVER_NAME']:
            urlparts_list = list(urlparts)
            urlparts_list[1] = app.config['SERVER_NAME']
            return redirect(urlunparse(urlparts_list), code=301)


@app.before_request
def before_request():
    if current_user.is_authenticated():
        g.user = current_user
    else:
        g.user = None


# ERROR HANDLERS
@app.errorhandler(404)
def page_not_found_error(error):
    return render_template(
        '404.html',
        title="Page Not Found",
        page_title="Page Not Found"
    ), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template(
        '500.html',
        title="Error",
        page_title="Error!"
    ), 500


# BASIC PAGES
@app.route('/how-it-works/', methods=['GET'])
def how_it_works():
    return render_template(
        'how_it_works.html',
        title="How " + app.config['APP_NAME'] + " Works",
        page_title="How " + app.config['APP_NAME'] + " Works"
    )


@app.route('/about/', methods=['GET'])
def about():
    return render_template(
        'about.html',
        title="About " + app.config['APP_NAME'],
        page_title="About " + app.config['APP_NAME']
    )


@app.route('/privacy/', methods=['GET'])
def privacy():
    return render_template(
        'privacy.html',
        title="Privacy Policy",
        page_title="Privacy Policy"
    )


# ADMIN LOGIN
@app.route('/admin-login/', methods=['GET', 'POST'])
def admin_login():
    if 'logged_in' in session:
        return redirect(url_for('admin.index'))
    form = LoginForm()
    if form.validate_on_submit():
        if request.form['username'] == app.config['ADMIN_USERNAME'] and \
                request.form['password'] == app.config['ADMIN_PASSWORD']:
            session['logged_in'] = True
            flash('Login successful.')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')
            return redirect(url_for('admin_login'))
    return render_template(
        'admin_login.html',
        title="Admin Login",
        page_title="Admin Login",
        form=form)


# ADMIN LOGOUT
@app.route('/admin-logout/')
@admin_login_required
def admin_logout():
    session.pop('logged_in', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))


# REDDIT LOGIN
@app.route('/login/')
def login():
    if current_user.is_anonymous():
        session['oauth_token'] = generate_token()
        oauth_link = r.get_authorize_url(
            session['oauth_token'],
            ['identity', 'submit', 'edit'],
            True
        )
        return render_template(
            'login.html',
            title="Reddit Login",
            page_title="Reddit Login",
            oauth_link=oauth_link
        )
    else:
        flash('You are already logged in!')
        return redirect(url_for('dashboard'))


# finish OAuth login
@app.route('/authorize/')
def authorize():
    state = request.args.get('state', '')
    if current_user.is_anonymous() and (state == session['oauth_token']):
        try:
            code = request.args.get('code', '')
            access_info = r.get_access_information(code)
            user_reddit = r.get_me()
            user = db.session.query(User)\
                .filter_by(username=user_reddit.name)\
                .first()
            if user is None:
                user = User(
                    username=user_reddit.name,
                    role_id=2,
                    refresh_token=access_info['refresh_token']
                )
                db.session.add(user)
                db.session.commit()
            else:
                user.refresh_token = access_info['refresh_token']
                db.session.commit()
            login_user(user)
            flash('Hi ' + user.username + '! You have successfully' +
                  ' logged in with your reddit account.')
            return redirect(url_for('dashboard'))
        except praw.errors.OAuthException:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('dashboard'))


# dashboard
@app.route('/dashboard/')
@login_required
def dashboard():
    active_threads = db.session.query(Thread)\
        .filter_by(user_id=g.user.id)\
        .filter_by(open_for_comments=True)\
        .all()
    inactive_threads = db.session.query(Thread)\
        .filter_by(user_id=g.user.id)\
        .filter_by(open_for_comments=False)\
        .all()
    return render_template(
        'dashboard.html',
        title="Your Dashboard",
        page_title="Your Dashboard",
        active_threads=active_threads,
        inactive_threads=inactive_threads
    )


# logout
@app.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))


# FRONT END
@app.route('/')
def index():
    threads = db.session.query(Thread)\
        .order_by(Thread.date_posted.desc())\
        .all()
    return render_template(
        'index.html',
        title='Create rating threads on reddit.',
        page_title='Latest Community Ratings',
        threads=threads
    )


# list categories
@app.route('/categories/')
def list_categories():
    categories = db.session.query(Category)\
        .all()
    return render_template(
        'list_categories.html',
        categories=categories,
        title="Categories",
        page_title="Categories"
    )


# category page
@app.route('/category/<category_slug>')
def category(category_slug):
    category = db.session.query(Category)\
        .filter_by(slug=category_slug)\
        .first()
    if category:
        threads = category.threads\
            .order_by(Thread.date_posted.desc())\
            .all()
        return render_template(
            'filtered_threads.html',
            threads=threads,
            title=category.name,
            page_title="Category: " + category.name
        )
    else:
        abort(404)


# list subreddits
@app.route('/subreddits/')
def list_subreddits():
    subreddits = db.session.query(Thread.subreddit).distinct()
    return render_template(
        'list_subreddits.html',
        subreddits=subreddits,
        title="Subreddits",
        page_title="Subreddits"
    )


# subreddit page
@app.route('/subreddit/<subreddit>')
def subreddit(subreddit):
    threads = db.session.query(Thread)\
        .filter_by(subreddit=subreddit)\
        .order_by(Thread.date_posted.desc())\
        .all()
    if threads:
        return render_template(
            'filtered_threads.html',
            threads=threads,
            title=subreddit,
            page_title="Subreddit: r/" + subreddit
        )
    else:
        abort(404)


# list tags
@app.route('/tags/')
def list_tags():
    tags = db.session.query(Tag).all()
    return render_template(
        'list_tags.html',
        tags=tags,
        title="Tags",
        page_title="Tags"
    )


# tag page
@app.route('/tag/<tag_slug>')
def tag(tag_slug):
    tag = db.session.query(Tag)\
        .filter_by(slug=tag_slug)\
        .first()
    if tag:
        threads = tag.threads\
            .order_by(Thread.date_posted.desc())\
            .all()
        return render_template(
            'filtered_threads.html',
            threads=threads,
            title=tag.name,
            page_title="Tag: " + tag.name
        )
    else:
        abort(404)


# thread single
@app.route('/<category_slug>/<thread_slug>/<thread_id>')
def thread(category_slug, thread_slug, thread_id):
    category = db.session.query(Category)\
        .filter_by(slug=category_slug)\
        .first()
    if category:
        thread = db.session.query(Thread)\
            .filter_by(id=thread_id)\
            .first()
        if thread:
            last_crawl = None
            comments = None
            if thread.comments:
                last_crawl = pretty_date(thread.last_crawl)
                comments = thread.comments\
                    .order_by(
                        (Comment.upvotes - Comment.downvotes).desc()
                    ).all()
            return render_template(
                'thread.html',
                thread=thread,
                last_crawl=last_crawl,
                comments=comments,
                title=thread.title
            )
        else:
            abort(404)
    else:
        abort(404)


# comment single
@app.route('/comment/<int:comment_id>')
def comment(comment_id):
    comment = db.session.query(Comment)\
        .filter_by(id=comment_id).first()
    if comment:
        return render_template(
            'comment.html',
            comment=comment,
            title="User Rating of " + comment.thread.title
        )
    else:
        abort(404)


# user profile
@app.route('/user/<username>')
def user_profile(username):
    user = db.session.query(User)\
        .filter_by(username=username).first()
    if user:
        threads = user.threads\
            .order_by(Thread.date_posted.desc())\
            .all()
        return render_template(
            'user_profile.html',
            user=user,
            threads=threads,
            title="User Profile: " + user.username,
            page_title="User Profile: " + user.username
        )
    else:
        abort(404)


# create thread form
@app.route('/create-thread/', methods=['GET', 'POST'])
@login_required
def create_thread():
    last_thread = g.user.threads\
        .order_by(Thread.date_posted.desc()).first()
    if last_thread is not None and last_thread.date_posted > \
            (datetime.utcnow() -
             timedelta(seconds=604800)) and 'logged_in' not in session:
        flash('Sorry, you can only create 1 rating per week.')
        return redirect(url_for('dashboard'))
    form = ThreadForm()
    categories = db.session.query(Category).order_by(Category.id.asc()).all()
    form.category.choices = [
        (cat.id, cat.name) for cat in categories
    ]
    form.category.choices.insert(0, (0, 'Choose one...'))
    if form.validate_on_submit():

        if not form.test_mode.data:

            # post to reddit
            reddit_post = None

            try:
                r.refresh_access_information(g.user.refresh_token)
                reddit_post = r.submit(
                    form.subreddit.data,
                    '[Community Rating] ' + form.reddit_title.data,
                    reddit_body(
                        form.description.data,
                        form.title.data
                    )
                )

                if reddit_post:
                    new_thread = Thread(
                        user_id=g.user.id,
                        title=form.title.data,
                        slug=make_slug(form.title.data),
                        category_id=form.category.data,
                        reddit_id=reddit_post.id,
                        reddit_permalink=reddit_post.permalink,
                        subreddit=form.subreddit.data,
                        date_posted=datetime.now(),
                        open_for_comments=True,
                        last_crawl=datetime.now()
                    )
                    db.session.add(new_thread)
                    db.session.commit()
                    success_message = Markup(
                        'Your rating thread has been '
                        'posted to reddit <a href="http://redd.it/' +
                        reddit_post.id +
                        '" target="_blank">here</a>.'
                    )
                    flash(success_message)

                    this_thread = db.session.query(Thread)\
                        .filter_by(reddit_id=reddit_post.id)\
                        .first()

                    return redirect(url_for(
                        'thread',
                        category_slug=this_thread.category.slug,
                        thread_slug=this_thread.slug,
                        thread_id=this_thread.id
                    ))

                else:
                    flash('Sorry, we could not create'
                          'your post on reddit. Try again later.')

            except praw.errors.APIException as e:
                flash('There was an error with your submission: ' +
                      e.message)

            except praw.errors.ClientException as e:
                flash('There was an error with your submission: ' +
                      e.message)

            except:
                error_message = Markup(
                    'Something went wrong. '
                    'Please try again or submit '
                    'an [Issue] to '
                    '<a href="http://reddit.com/r/redditratings" '
                    'target="_blank">/r/RedditRatings</a>.')
                flash(error_message)
        else:
            new_thread = Thread(
                user_id=g.user.id,
                title=form.title.data,
                category_id=form.category.data,
                subreddit=form.subreddit.data,
                date_posted=datetime.now(),
                open_for_comments=True
            )
            db.session.add(new_thread)
            db.session.commit()
            flash('Your rating thread has been created.')

            this_thread = db.session.query(Thread)\
                .filter_by(category_id=form.category.data)\
                .filter_by(title=form.title.data)\
                .first()

            return redirect(url_for(
                'thread',
                category_slug=this_thread.category.slug,
                thread_slug=this_thread.slug,
                thread_id=this_thread.id
            ))

    return render_template(
        'create_thread.html',
        title="Create a Community Rating on reddit",
        page_title="Create a Community Rating on reddit",
        form=form
    )


# edit thread form
@app.route('/edit-thread/<int:thread_id>', methods=['GET', 'POST'])
@login_required
def edit_thread(thread_id):
    thread = db.session.query(Thread)\
        .filter_by(id=thread_id)\
        .first()
    if thread:
        if thread.open_for_comments:
            if thread.user.username == g.user.username:
                form = EditThreadForm(obj=thread)
                categories = db.session.query(Category)\
                    .order_by(Category.id.asc()).all()
                form.category.choices = [
                    (cat.id, cat.name) for cat in categories
                ]

                if form.validate_on_submit():
                    thread.category_id = form.category.data
                    db.session.commit()
                    flash('Your rating category has been updated.')
                    return redirect(url_for(
                        'thread',
                        category_slug=thread.category.slug,
                        thread_slug=thread.slug,
                        thread_id=thread.id
                    ))

                form.category.data = thread.category_id

                return render_template(
                    'edit_thread.html',
                    title="Edit \"" + thread.title + "\"",
                    page_title="Edit \"" + thread.title + "\"",
                    form=form,
                    thread=thread
                )
            else:
                flash("Sorry, you cannot edit a rating you didn't create!")
                return redirect(url_for('index'))
        else:
            flash('This rating is not editable because it is closed.')
            return redirect(url_for(
                'thread',
                category_slug=thread.category.slug,
                thread_slug=thread.slug,
                thread_id=thread.id
            ))
    else:
        abort(404)


# close thread
@app.route('/close-thread/<int:thread_id>', methods=['GET', 'POST'])
@login_required
def close_thread(thread_id):
    thread = db.session.query(Thread)\
        .filter_by(id=thread_id)\
        .first()
    if thread:
        if thread.open_for_comments:
            if thread.user.username == g.user.username:
                form = CloseThreadForm()
                if form.validate_on_submit():

                    thread.open_for_comments = False
                    db.session.commit()

                    # edit reddit thread
                    r.refresh_access_information(g.user.refresh_token)

                    try:
                        submission = r.get_submission(
                            submission_id=thread.reddit_id
                        )
                        if submission.selftext:
                            new_selftext = '**Edit:** This rating thread has been ' + \
                                ' closed. Thanks for participating!\n\n' + \
                                submission.selftext
                            submission.edit(new_selftext)
                    except HTTPError:
                        flash('We could not edit your reddit thread. '
                              'Please edit it so other users know it is closed.')

                    success_message = Markup(
                        'This rating has been closed and '
                        '<a href="http://redd.it/' +
                        thread.reddit_id +
                        '" target="_blank">updated on reddit</a>.'
                    )

                    flash(success_message)
                    return redirect(url_for(
                        'thread',
                        category_slug=thread.category.slug,
                        thread_slug=thread.slug,
                        thread_id=thread.id
                    ))

            else:
                return redirect(url_for('index'))

            return render_template(
                'close_thread.html',
                title='Close Thread',
                page_title='Are you sure you want to close "'
                + thread.title + '"?',
                form=form,
                thread=thread
            )
        else:
            flash('This rating  has already been closed.')
            return redirect(url_for(
                'thread',
                category_slug=thread.category.slug,
                thread_slug=thread.slug
            ))
    else:
        abort(404)
