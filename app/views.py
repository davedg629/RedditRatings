from app import app, db
from flask import flash, redirect, render_template, request, \
    session, url_for, g
from app.forms import LoginForm
from app.models import Category, Role, User, Group, CommunityReview, \
    UserReview
from datetime import datetime
from app.utils import make_slug, get_avg_rating, get_review_count, \
    pretty_date
from app.decorators import login_required


# ERROR HANDLERS
@app.errorhandler(404)
def page_not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


# BASIC PAGES
@app.route('/how-it-works/', methods=['GET'])
def how_it_works():
    return render_template('how_it_works.html',
                           title="How Reddit Game Reviews Works"
                           )


@app.route('/about/', methods=['GET'])
def about():
    return render_template('about.html',
                           title="About Reddit Game Reviews"
                           )


# LOGIN AND LOGOUT
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return redirect(url_for('admin.index'))
    form = LoginForm()
    error = None
    if form.validate_on_submit():
        if request.form['username'] == app.config['ADMIN_USERNAME'] and \
                request.form['password'] == app.config['ADMIN_PASSWORD']:
            session['logged_in'] = True
            flash('Login successful.')
            return redirect(url_for('admin.index'))
        else:
            error = 'Invalid username or password.'
    return render_template('login.html',
                           title="Login", form=form, error=error)


@app.route('/logout/')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))


# FRONT END
@app.route('/')
def index():
    community_reviews = db.session.query(CommunityReview).order_by(
        CommunityReview.date_posted.desc()
    ).all()
    return render_template(
        'index.html',
        community_reviews=community_reviews
    )


@app.route('/<platform_slug>/<game_slug>/<int:community_review_id>')
def community_review(platform_slug, game_slug, community_review_id):
    community_review = db.session.query(CommunityReview)\
        .filter_by(id=community_review_id).first()
    if community_review and community_review.game.slug == game_slug \
            and community_review.game.platform.slug == platform_slug:
        last_crawl = None
        avg_rating = None
        user_reviews = None
        user_reviews_count = 0
        if community_review.user_reviews:
            last_crawl = pretty_date(community_review.last_crawl)
            avg_rating = get_avg_rating(community_review.id)
            user_reviews = db.session.query(UserReview)\
                .filter_by(community_review_id=community_review.id)\
                .order_by(UserReview.reddit_score.desc())
            user_reviews_count = get_review_count(community_review.id)
        return render_template('community_review.html',
                               community_review=community_review,
                               avg_rating=avg_rating,
                               last_crawl=last_crawl,
                               user_reviews=user_reviews,
                               user_reviews_count=user_reviews_count
                               )
    else:
        return render_template('404.html')


@app.route('/user-review/<int:user_review_id>')
def user_review(user_review_id):
    user_review = db.session.query(UserReview)\
        .filter_by(id=user_review_id).first()
    if user_review:
        return render_template('user_review.html',
                               user_review=user_review
                               )
    else:
        return render_template('404.html')
