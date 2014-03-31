from app import app, db
from flask import flash, redirect, render_template, request, \
    session, url_for, abort
from app.forms import LoginForm
from app.models import Category, Tag, CommunityReview, \
    UserReview, User
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
    community_reviews = db.session.query(CommunityReview)\
        .order_by(CommunityReview.date_posted.desc())\
        .all()
    return render_template(
        'index.html',
        title='Creating reviews together, on reddit.',
        page_title='Latest Community Ratings',
        community_reviews=community_reviews
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
        community_reviews = category.community_reviews\
            .order_by(CommunityReview.date_posted.desc())\
            .all()
        return render_template(
            'filtered_community_reviews.html',
            community_reviews=community_reviews,
            title=category.name,
            page_title="Category: " + category.name
        )
    else:
        abort(404)


# list subreddits
@app.route('/subreddits/')
def list_subreddits():
    subreddits = db.session.query(CommunityReview.subreddit).distinct()
    return render_template(
        'list_subreddits.html',
        subreddits=subreddits,
        title="Subreddits",
        page_title="Subreddits"
    )


# subreddit page
@app.route('/subreddit/<subreddit>')
def subreddit(subreddit):
    community_reviews = db.session.query(CommunityReview)\
        .filter_by(subreddit=subreddit)\
        .order_by(CommunityReview.date_posted.desc())\
        .all()
    if community_reviews:
        return render_template(
            'filtered_community_reviews.html',
            community_reviews=community_reviews,
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
        community_reviews = tag.community_reviews\
            .order_by(CommunityReview.date_posted.desc())\
            .all()
        return render_template(
            'filtered_community_reviews.html',
            community_reviews=community_reviews,
            title=tag.name,
            page_title="Tag: " + tag.name
        )
    else:
        abort(404)


# community review single
@app.route('/<category_slug>/<community_review_slug>')
def community_review(category_slug, community_review_slug):
    category = db.session.query(Category)\
        .filter_by(slug=category_slug)\
        .first()
    if category:
        community_review = db.session.query(CommunityReview)\
            .filter_by(category_id=category.id)\
            .filter_by(slug=community_review_slug)\
            .first()
        if community_review:
            last_crawl = None
            user_reviews = None
            if community_review.user_reviews:
                last_crawl = pretty_date(community_review.last_crawl)
                user_reviews = community_review.user_reviews\
                    .order_by(
                        (UserReview.upvotes - UserReview.downvotes).desc()
                    ).all()
            return render_template(
                'community_review.html',
                community_review=community_review,
                last_crawl=last_crawl,
                user_reviews=user_reviews,
                title=community_review.title
            )
        else:
            abort(404)
    else:
        abort(404)


# user review single
@app.route('/user-review/<int:user_review_id>')
def user_review(user_review_id):
    user_review = db.session.query(UserReview)\
        .filter_by(id=user_review_id).first()
    if user_review:
        return render_template(
            'user_review.html',
            user_review=user_review,
            title="User Rating of " + user_review.community_review.title
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
