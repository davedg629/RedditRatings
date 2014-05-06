from app import db
from app.models import User, Thread, Comment
from config import REDDIT_USERNAME, REDDIT_PASSWORD, \
    REDDIT_USER_AGENT, SERVER_NAME
from app.utils import is_number
import praw
import datetime
import time
from requests import HTTPError
from flask.ext.script import Command, Option


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


def parse_comment_body(labelPos, label, comment_body):
    """Parses comment body, given the label,
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
        body = \
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
        body = \
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
        body = \
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

    return body.replace("\n", "<br />")


def parse_comment(comment_body, body_label):
    """Takes a reddit comment and pulls out rating details"""
    labels = [
        'rating',
        body_label
    ]

    comment_params = {}

    for label in labels:

        labelPos = comment_body.lower().find(label + ':')
        if labelPos >= 0:

            # parse rating
            if label == 'rating':
                comment_params[label] = \
                    parse_comment_rating(labelPos, label, comment_body)

            # parse comment body
            else:
                comment_params[label] = \
                    parse_comment_body(labelPos, label, comment_body)

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


def update_comment(comment_body, comment_edited, reddit_id, body_label):
    """Update a comment and last_edited value."""
    label = body_label
    labelPos = comment_body.lower().find(label)
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
            editedComment = \
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
            editedComment = \
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
            editedComment = \
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
        editedComment = ''

    db.session.query(Comment)\
        .filter_by(reddit_id=reddit_id)\
        .update({
            "body": editedComment.replace("\n", "<br />"),
            "edited_stamp": comment_edited
        })
    db.session.commit()


def send_pm(author, thread, r):
    r.send_message(
        author,
        'Success!',
        'Your rating of **' + thread.title +
        '** has been successfully added.' +
        '\n\nView the Community Rating here: ' +
        'http://' + SERVER_NAME + '/' +
        thread.category.slug + '/' +
        thread.slug +
        '\n\n(You received this message because you ' +
        'included a \'verifyrating\' tag in your ' +
        'rating.)'
    )


class Crawl(Command):
    "Crawl open Threads"

    option_list = (
        Option('--silent', '-s', dest='silent'),
        Option('--label', '-l', dest='body_label'),
    )

    def run(self, silent, body_label):

        # get reddit user agent
        user_agent = (REDDIT_USER_AGENT)

        # create praw instance with user agent
        r = praw.Reddit(user_agent=user_agent)

        # login with reddit username/password
        r.login(REDDIT_USERNAME, REDDIT_PASSWORD)

        # get all threads uploaded to site
        threads = db.session.query(Thread)\
            .filter_by(open_for_comments=True)\
            .filter(Thread.reddit_id != '')\
            .all()

        # get comments for each thread
        for thread in threads:

            # get submission from reddit, store comments in variable
            try:
                submission = r.get_submission(
                    submission_id=thread.reddit_id
                )
                submission.replace_more_comments(limit=None, threshold=0)
                top_lvl_comments = submission.comments
            except HTTPError:
                continue

            for comment in top_lvl_comments:

                if comment.author:

                    # check if this comment has already been parsed
                    this_comment = db.session.query(Comment)\
                        .filter_by(reddit_id=comment.id).first()

                    # get time since comment was created
                    t = datetime.datetime.now()
                    time_since_created = \
                        time.mktime(t.timetuple()) - comment.created_utc

                    # has the comment not been parsed yet and
                    # is it at least 3 minutes old
                    if not this_comment and time_since_created > 180:

                        # check if this user has already commented
                        # on this thread
                        this_user_check = None
                        this_user = db.session.query(User)\
                            .filter_by(username=comment.author.name)\
                            .first()
                        if this_user:
                            this_user_check = db.session.query(Comment)\
                                .filter_by(
                                    thread_id=thread.id
                                )\
                                .filter_by(user_id=this_user.id)\
                                .first()

                        if not this_user_check:

                            if 'rating:' in comment.body.lower():

                                # parse comment
                                comment_params = parse_comment(comment.body, body_label)

                                if 1 <= comment_params['rating'] <= 10:

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

                                    # add comment to db
                                    new_comment = Comment(
                                        thread_id=thread.id,
                                        user_id=user_id,
                                        reddit_id=comment.id,
                                        date_posted=datetime.datetime
                                        .utcfromtimestamp(comment.created_utc),
                                        rating=comment_params['rating'],
                                        body=comment_params[body_label],
                                        upvotes=comment.ups,
                                        downvotes=comment.downs,
                                        edited_stamp=this_last_edited
                                    )
                                    db.session.add(new_comment)
                                    db.session.commit()

                                    # reply with a success message if user wants it
                                    if 'verifyrating' in comment.body.lower() \
                                            and silent != 'true':
                                        send_pm(
                                            comment.author.name,
                                            thread,
                                            r
                                        )

                    # is the comment already in the db
                    elif this_comment:

                        if time_since_created < 3600:

                            if comment.edited > this_comment.edited_stamp:
                                update_comment(
                                    comment.body,
                                    comment.edited,
                                    comment.id,
                                    body_label
                                )

                        if comment.ups != this_comment.upvotes:
                            this_comment.upvotes = comment.ups
                            db.session.commit()
                        if comment.downs != this_comment.downvotes:
                            this_comment.downvotes = comment.downs
                            db.session.commit()

            # update last_crawl and up/downvotes for thread
            thread.last_crawl = datetime.datetime.now()
            if thread.upvotes != submission.ups:
                thread.upvotes = submission.ups
            if thread.downvotes != submission.downs:
                thread.downvotes = submission.downs
            db.session.commit()

            # update results on reddit
            if submission.selftext and thread.get_comment_count() != 0:
                results_label_pos = submission.selftext.lower().find(
                    '**live results**'
                )
                if results_label_pos > 0:
                    results_start_pos = submission.selftext.lower()\
                        .find('[', results_label_pos)
                    results_end_pos = submission.selftext.lower()\
                        .find(']', results_label_pos)
                    results_string = \
                        submission.selftext[
                            results_start_pos + 1:results_end_pos
                        ]
                    new_comment_cnt = thread.get_comment_count()
                    if new_comment_cnt == '1':
                        comment_cnt_suffix = 'rating'
                    else:
                        comment_cnt_suffix = 'ratings'
                    new_avg_rating = thread.get_avg_rating()
                    new_reddit_body = submission.selftext.replace(
                        results_string,
                        new_avg_rating +
                        ' out of 10, based on ' +
                        new_comment_cnt + ' ' + comment_cnt_suffix
                    )
                    submission.edit(new_reddit_body)

                else:
                    thread.open_for_comments = False
                    db.session.commit()

            else:
                thread.open_for_comments = False
                db.session.commit()
