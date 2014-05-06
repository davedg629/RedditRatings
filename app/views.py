from app import app, db
from flask import flash, redirect, render_template, request, \
    session, url_for, abort, Markup
from app.forms import LoginForm, ThreadForm, EditThreadForm, \
    CloseThreadForm
from app.models import Category, Tag, Thread, \
    Comment, User
from app.utils import pretty_date, reddit_body
from app.decorators import login_required
from datetime import datetime
import praw
from app.utils import make_slug
from sqlalchemy.sql import func

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


# LOGIN
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return redirect(url_for('admin.index'))
    form = LoginForm()
    if form.validate_on_submit():
        if request.form['username'] == app.config['ADMIN_USERNAME'] and \
                request.form['password'] == app.config['ADMIN_PASSWORD']:
            session['logged_in'] = True
            flash('Login successful.')
            return redirect(url_for('admin.index'))
        else:
            flash('Invalid username or password.')
            return redirect(url_for('login'))
    return render_template(
        'login.html',
        title="Admin Login",
        page_title="Login",
        form=form)


# LOGOUT
@app.route('/logout/')
@login_required
def logout():
    session.pop('logged_in', None)
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
        title='Creating ratings on reddit, together.',
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
@app.route('/<category_slug>/<thread_slug>')
def thread(category_slug, thread_slug):
    category = db.session.query(Category)\
        .filter_by(slug=category_slug)\
        .first()
    if category:
        thread = db.session.query(Thread)\
            .filter_by(category_id=category.id)\
            .filter_by(slug=thread_slug)\
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
    form = ThreadForm()
    categories = db.session.query(Category).order_by(Category.id.asc()).all()
    form.category.choices = [
        (cat.id, cat.name) for cat in categories
    ]
    if form.validate_on_submit():

        if form.test_mode.data:

            # post to reddit
            r = praw.Reddit(user_agent=app.config['REDDIT_USER_AGENT'])
            reddit_post = None

            # create a unique slug from the thread title
            new_slug = make_slug(form.title.data)
            slug_check = None
            slug_check = db.session.query(Thread)\
                .filter_by(category_id=form.category.data)\
                .filter_by(title=form.title.data).first()

            if slug_check:
                same_slug_count = db.session\
                    .query(func.count(Thread.id))\
                    .filter_by(
                        category_id=form.category.data
                    )\
                    .filter_by(title=form.title.data)
                new_slug = new_slug + '-' + str(same_slug_count[0][0] + 1)

            # get the category slug
            category = db.session.query(Category)\
                .filter_by(id=form.category.data)\
                .first()

            try:
                r.login(
                    app.config['REDDIT_USERNAME'],
                    app.config['REDDIT_PASSWORD']
                )
                reddit_post = r.submit(
                    form.subreddit.data,
                    '[Community Rating] ' + form.title.data,
                    reddit_body(
                        form.description.data,
                        form.title.data,
                        category.slug,
                        new_slug
                    )
                )

                if reddit_post:
                    new_thread = Thread(
                        user_id=1,
                        title=form.title.data,
                        slug=new_slug,
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
                        thread_slug=this_thread.slug
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
                user_id=1,
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
                thread_slug=this_thread.slug
            ))

    return render_template(
        'create_thread.html',
        title="Create a Community Rating thread on reddit",
        page_title="Create a Community Rating thread on reddit",
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
        form = EditThreadForm(obj=thread)
        categories = db.session.query(Category)\
            .order_by(Category.id.asc()).all()
        form.category.choices = [
            (cat.id, cat.name) for cat in categories
        ]

        if form.validate_on_submit():
            thread.category_id = form.category.data
            db.session.commit()

            return redirect(url_for(
                'thread',
                category_slug=thread.category.slug,
                thread_slug=thread.slug
            ))

        return render_template(
            'edit_thread.html',
            title="Edit \"" + thread.title + "\"",
            page_title="Edit \"" + thread.title + "\"",
            form=form,
            thread=thread
        )
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
            form = CloseThreadForm()
            if form.validate_on_submit():
                thread.open_for_comments = False
                db.session.commit()
                return redirect(url_for(
                    'user_profile',
                    username=thread.user.username
                ))

            return render_template(
                'close_thread.html',
                title='Close Thread',
                page_title='Are you sure you want to close "'
                + thread.title + '"?',
                form=form,
                thread=thread
            )
        else:
            flash('This ratings thread has already been closed')
            return redirect(url_for(
                'thread',
                category_slug=thread.category.slug,
                thread_slug=thread.slug
            ))
    else:
        abort(404)
