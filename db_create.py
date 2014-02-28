from app import db
from app.models import Category, Role, User, Group, CommunityReview, UserReview
from datetime import datetime, date

db.create_all()

## users
#db.session.add(
#    User(
#        username="redditreviewbot"
#    )
#)
#
## community reviews
#db.session.add(
#    CommunityReview(
#        game_id=1,
#        user_id=1,
#        reddit_id="1ycqin",
#        reddit_permalink="http://www.reddit.com/r/3DS/comments/1ycqin/i_created_an_app_that_allows_us_to_review_games/",
#        subreddit="3ds",
#        date_posted=datetime(2014, 2, 19),
#        open_for_comments=True,
#        last_crawl=datetime.now()
#    )
#)
#
## user reviews
##db.session.add(
##    UserReview(
##        community_review_id=1,
##        user_id=1,
##        reddit_id="cfjcvxe",
##        date_posted=datetime(2014, 2, 19),
##        rating=10,
##        review="Ultimated the successor to Final Fantasy...",
##        reddit_score=8,
#        edited=1
#    )
#)

db.session.commit()
