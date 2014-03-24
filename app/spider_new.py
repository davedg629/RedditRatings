from app import db
from app.models import User, CommunityReview, UserReview
from config import REDDIT_USERNAME, REDDIT_PASSWORD, \
    REDDIT_USER_AGENT, SERVER_NAME
from app.utils import is_number
import praw
import datetime
import time
from requests import HTTPError
from flask.ext.script import Command


def parse_comment_rating(labelPos, label, comment_body):
    """Parse rating from comment, given the rating label,
    label position, and the comment body."""

    for i in range(labelPos + len(label) + 1,
                   labelPos + len(label) + 5):
        if is_number(comment_body[i]):
            if comment_body[i] == '1' \
                    and comment_body[i + 1] == '0':
                return int(comment_body[i:i + 2])
            else:
                return int(comment_body[i])

    return 0


def parse_comment_review(labelPos, label, comment_body):
    """Parse review from comment, given the review label,
    label position, and comment body."""

    if comment_body.find('---', labelPos) > 0:
        endPos = comment_body.find('---', labelPos)
    elif comment_body.find('___', labelPos) > 0:
        endPos = comment_body.find('___', labelPos)
    elif comment_body.find('***', labelPos) > 0:
        endPos = comment_body.find('***', labelPos)
    else:
        endPos = -1

    if comment_body[labelPos - 2:
                    labelPos +
                    len(label) + 3] == '**' + label + ':**':
        review_body = \
            comment_body[
                labelPos +
                len(label) +
                + 3:endPos
            ].strip() \
            if endPos != -1 else \
            comment_body[
                labelPos +
                len(label) +
                + 3:
            ].strip()

    elif comment_body[labelPos - 1:
                      labelPos +
                      len(label) + 2] == '*' + label + ':*':
        review_body = \
            comment_body[
                labelPos +
                len(label) +
                + 2:endPos
            ].strip() \
            if endPos != -1 else \
            comment_body[
                labelPos +
                len(label) +
                + 2:
            ].strip()

    else:
        review_body = \
            comment_body[
                labelPos +
                len(label) +
                + 1:endPos
            ].strip() \
            if endPos != -1 else \
            comment_body[
                labelPos +
                len(label) +
                + 1:
            ].strip()

    return review_body.replace("\n", "<br />")


def parse_comment(comment_body):
    """Takes a reddit comment and pulls out rating details"""
    labels = [
        'Rating',
        'Review'
    ]

    comment_params = {}

    for label in labels:

        labelPos = comment_body.find(label + ':')
        if labelPos >= 0:

            # parse Rating
            if label == 'Rating':
                comment_params[label] = \
                    parse_comment_rating(labelPos, label, comment_body)

            # parse Review
            else:
                comment_params[label] = \
                    parse_comment_review(labelPos, label, comment_body)

        else:
            comment_params[label] = ''

    return comment_params


def add_user(username):
    """Adds user to database and returns user id if not already in database"""
    # check if user already exists in db
    user_check = db.session.query(User).filter_by(
        username=username).first()

    # if user not in db, add to db
    if not user_check:
        new_user = User(
            username=username,
            role_id=2
        )
        db.session.add(new_user)
        db.session.commit()
        user = db.session.query(User)\
            .filter_by(username=username).first()
        return user.id

    return user_check.id


def update_review(comment_body, comment_edited, reddit_id):
    """Update a review from reddit comment
    and update last_edited value in db for the review."""
    label = 'Review'
    labelPos = comment_body.find(label)
    if labelPos >= 0:

        if comment_body.find('---', labelPos) > 0:
            endPos = comment_body.find('---', labelPos)
        elif comment_body.find('___', labelPos) > 0:
            endPos = comment_body.find('___', labelPos)
        elif comment_body.find('***', labelPos) > 0:
            endPos = comment_body.find('***', labelPos)
        else:
            endPos = -1

        if comment_body[labelPos - 2:
                        labelPos +
                        len(label) + 3] == '**' + label + ':**':
            editedReview = \
                comment_body[
                    labelPos +
                    len(label) +
                    + 3:endPos
                ].strip() \
                if endPos != -1 else \
                comment_body[
                    labelPos +
                    len(label) +
                    + 3:
                ].strip()

        elif comment_body[labelPos - 1:
                          labelPos +
                          len(label) + 2] == '*' + label + ':*':
            editedReview = \
                comment_body[
                    labelPos +
                    len(label) +
                    + 2:endPos
                ].strip() \
                if endPos != -1 else \
                comment_body[
                    labelPos +
                    len(label) +
                    + 2:
                ].strip()

        else:
            editedReview = \
                comment_body[
                    labelPos +
                    len(label) +
                    + 1:endPos
                ].strip() \
                if endPos != -1 else \
                comment_body[
                    labelPos +
                    len(label) +
                    + 1:
                ].strip()
    else:
        editedReview = ''

    db.session.query(UserReview)\
        .filter_by(reddit_id=reddit_id)\
        .update({
            "review": editedReview.replace("\n", "<br />"),
            "edited_stamp": comment_edited
        })
    db.session.commit()


def send_pm(author, community_review, r):
    r.send_message(
        author,
        'Success!',
        'Your review of **' + community_review.title +
        '** has been successfully added.' +
        '\n\nView the Community Review here: ' +
        'http://' + SERVER_NAME + '/' +
        community_review.category.slug + '/' +
        community_review.slug +
        '\n\n(You received this message because you ' +
        'included a \'verifyreview\' tag in your ' +
        'review.)'
    )


class Crawl(Command):
    "Crawl open Community Reviews"

    def run(self):

        # get reddit user agent
        user_agent = (REDDIT_USER_AGENT)

        # create praw instance with user agent
        r = praw.Reddit(user_agent=user_agent)

        # login with reddit username/password
        r.login(REDDIT_USERNAME, REDDIT_PASSWORD)

        # get all reviews uploaded to site
        community_reviews = db.session.query(CommunityReview)\
            .filter_by(open_for_comments=True)\
            .filter(CommunityReview.reddit_id != '')\
            .all()

        # get comments for each review
        for community_review in community_reviews:

            # get submission from reddit, store comments in variable
            try:
                submission = r.get_submission(
                    submission_id=community_review.reddit_id
                )
                submission.replace_more_comments(limit=None, threshold=0)
                top_lvl_comments = submission.comments
            except HTTPError:
                continue

            for comment in top_lvl_comments:

                if comment.author:

                    # check if this comment has already been parsed
                    this_comment = db.session.query(UserReview)\
                        .filter_by(reddit_id=comment.id).first()

                    # get time since comment was created
                    t = datetime.datetime.now()
                    time_since_created = \
                        time.mktime(t.timetuple()) - comment.created_utc

                    # has the comment not been parsed yet and
                    # is it at least 3 minutes old
                    if not this_comment and time_since_created > 180:

                        # check if this user has already commented
                        # on this review
                        this_user_check = None
                        this_user = db.session.query(User)\
                            .filter_by(username=comment.author.name)\
                            .first()
                        if this_user:
                            this_user_check = db.session.query(UserReview)\
                                .filter_by(
                                    community_review_id=community_review.id
                                )\
                                .filter_by(user_id=this_user.id)\
                                .first()

                        if not this_user_check:

                            if 'Rating:' in comment.body:

                                # parse comment
                                comment_params = parse_comment(comment.body)

                                if 1 <= comment_params['Rating'] <= 10:

                                    # add user if not already in db and get user_id
                                    if not this_user:
                                        user_id = add_user(comment.author.name)
                                    else:
                                        user_id = this_user.id

                                    # make sure last_edited value is an int
                                    if not comment.edited:
                                        this_last_edited = 0
                                    else:
                                        this_last_edited = comment.edited

                                    # add comment to db as a user review
                                    new_user_review = UserReview(
                                        community_review_id=community_review.id,
                                        user_id=user_id,
                                        reddit_id=comment.id,
                                        date_posted=datetime.datetime
                                        .utcfromtimestamp(comment.created_utc),
                                        rating=comment_params['Rating'],
                                        review=comment_params['Review'],
                                        upvotes=comment.ups,
                                        downvotes=comment.downs,
                                        edited_stamp=this_last_edited
                                    )
                                    db.session.add(new_user_review)
                                    db.session.commit()

                                    # reply with a success message if user wants it
                                    if ('verifyreview' in comment.body) \
                                            or ('VerifyReview' in comment.body):
                                        send_pm(
                                            comment.author.name,
                                            community_review,
                                            r
                                        )

                    # is the comment already in the db
                    elif this_comment:

                        if time_since_created < 3600:

                            if comment.edited > this_comment.edited_stamp:
                                update_review(
                                    comment.body,
                                    comment.edited,
                                    comment.id
                                )

                        if comment.ups != this_comment.upvotes:
                            this_comment.upvotes = comment.ups
                            db.session.commit()
                        if comment.downs != this_comment.downvotes:
                            this_comment.downvotes = comment.downs
                            db.session.commit()

            # update last_crawl and up/downvotes for review
            community_review.last_crawl = datetime.datetime.now()
            if community_review.upvotes != submission.ups:
                community_review.upvotes = submission.ups
            if community_review.downvotes != submission.downs:
                community_review.downvotes = submission.downs
            db.session.commit()
