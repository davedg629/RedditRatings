from app import app, db
from flask import flash, redirect, render_template, request, \
    session, url_for, abort
from app.forms import LoginForm
from app.models import Category, Tag, Thread, \
    Comment, User
from app.utils import pretty_date
from app.decorators import login_required


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


# LOGIN AND LOGOUT
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
        return render_template(
            'user_profile.html',
            user=user,
            title="User Profile: " + user.username,
            page_title="User Profile: " + user.username
        )
    else:
        abort(404)
