from app import db
from app.models import Category, Role, User, Tag, CommunityReview, UserReview
from datetime import datetime

db.create_all()

db.session.add(
    Category(
        name='Video Games',
        slug='video-games'
    )
)

db.session.add(
    Category(
        name='Movies',
        slug='movies'
    )
)
db.session.add(
    Category(
        name='Podcasts',
        slug='podcasts'
    )
)
db.session.add(
    Category(
        name='Books',
        slug='books'
    )
)
db.session.add(
    Category(
        name='Music',
        slug='music'
    )
)
db.session.add(
    Category(
        name='TV',
        slug='tv'
    )
)
db.session.add(
    Category(
        name='Products',
        slug='products'
    )
)
db.session.add(
    Category(
        name='Food',
        slug='food'
    )
)
db.session.add(
    Category(
        name='People',
        slug='people'
    )
)
db.session.add(
    Category(
        name='Other',
        slug='other'
    )
)

db.session.add(
    Role(
        name='Admin'
    )
)
db.session.add(
    Role(
        name='User'
    )
)

db.session.add(
    User(
        username="redditreviewbot",
        role_id=1
    )
)

tag1 = Tag(
    name="Joe Rogan Experience",
    slug="joe-rogan-experience"
)

tag2 = Tag(
    name="Nintendo 3DS",
    slug="nintendo-3ds"
)


db.session.add(tag1)
db.session.add(tag2)

community_review1 = CommunityReview(
    user_id=1,
    title=u'Bravely Default - 3DS',
    category_id=1,
    reddit_id="1ycqin",
    reddit_permalink="http://www.reddit.com/r/3DS/comments/1ycqin/i_created_an_app_that_allows_us_to_review_games/",
    subreddit="3DS",
    link_url="http://bravelydefault.nintendo.com/",
    link_text="Official Website for Bravely Default",
    date_posted=datetime(2014, 2, 19),
    open_for_comments=False,
    last_crawl=datetime.now()
)
community_review1.tags.append(tag2)
db.session.add(community_review1)

community_review2 = CommunityReview(
    user_id=1,
    title=u'Test',
    category_id=10,
    reddit_id="1zqzcs",
    reddit_permalink="http://www.reddit.com/r/redditreviewbot/comments/1zqzcs/community_review_this_is_a_test/",
    subreddit="RedditReviewBot",
    link_url="http://reddit.com/user/redditreviewbot",
    link_text="RedditReviewBot User Page",
    date_posted=datetime(2014, 2, 19),
    open_for_comments=False,
    last_crawl=datetime.now()
)
db.session.add(community_review2)

## user reviews
##db.session.add(
##    UserReview(
##        community_review_id=1,
##        user_id=1,
##        reddit_id="cfjcvxe",
##        date_posted=datetime(2014, 2, 19),
##        rating=10,
##        review="Ultimated the successor to Final Fantasy...",
##        upvotes=1,
##        downvotes=0,
#        edited=1
#    )
#)

db.session.commit()
