from app import db
from app.models import User, Thread, Comment
from config import REDDIT_USER_AGENT, REDDIT_APP_ID, \
    REDDIT_APP_SECRET, OAUTH_REDIRECT_URI, SERVER_NAME, \
    REDDIT_USERNAME, REDDIT_PASSWORD
import praw
import datetime
import time
from requests import HTTPError
from flask.ext.script import Command, Option


def parse_comment(comment_body):
    """Takes a reddit comment and pulls out rating details"""
    comment_params = {}

    split_body = comment_body.split(None, 1)

    try:
        comment_params['rating'] = round(float(split_body[0]), 1)
    except:
        comment_params['rating'] = False

    if comment_params['rating'] is not False \
            and (0 <= comment_params['rating'] <= 10):
        if len(split_body) > 1:
            comment = split_body[1]
            if comment.find('---') == 0 or comment.find('___') == 0 \
                    or comment.find('***') == 0:
                comment_params['comment'] = ''
            else:
                if comment.find('---') > 0:
                    comment = comment[0:comment.find('---')]
                elif comment.find('___') > 0:
                    comment = comment[0:comment.find('___')]
                elif comment.find('***') > 0:
                    comment = comment[0:comment.find('***')]

                comment_params['comment'] = \
                    comment.strip().replace("\n", "<br />")

        else:
            comment_params['comment'] = ''

    else:
        comment_params['rating'] = False
        comment_params['comment'] = ''

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


def update_comment(comment_body):
    """Update a comment and last_edited value."""

    split_body = comment_body.split(None, 1)

    if len(split_body) > 1:
        comment = split_body[1]
        if comment.find('---') == 0 or comment.find('___') == 0 \
                or comment.find('***') == 0:
            comment = ''
        else:
            if comment.find('---') > 0:
                comment = comment[0:comment.find('---')]
            elif comment.find('___') > 0:
                comment = comment[0:comment.find('___')]
            elif comment.find('***') > 0:
                comment = comment[0:comment.find('***')]

            comment = comment.strip().replace("\n", "<br />")

    else:
        comment = ''

    return comment


def send_pm(author, thread, r):
    #admin_user = db.session.query(User)\
    #    .filter_by(id=1).first()
    r.login(REDDIT_USERNAME, REDDIT_PASSWORD)
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
        Option('--expire', '-e', dest='expire'),
    )

    def run(self, silent, expire):

        # get reddit user agent
        user_agent = (REDDIT_USER_AGENT)

        # create praw instance with user agent
        r = praw.Reddit(user_agent=user_agent)
        r.set_oauth_app_info(
            REDDIT_APP_ID,
            REDDIT_APP_SECRET,
            OAUTH_REDIRECT_URI
        )

        # get all threads uploaded to site
        threads = db.session.query(Thread)\
            .filter_by(open_for_comments=True)\
            .filter(Thread.reddit_id != '')\
            .all()

        # get comments for each thread
        for thread in threads:

            # get submission from reddit, store comments in variable
            try:
                r.refresh_access_information(
                    thread.user.refresh_token
                )
                submission = r.get_submission(
                    submission_id=thread.reddit_id
                )
                if submission.author is None:
                    thread.open_for_comments = False
                    db.session.commit()
                    continue
                else:
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

                            # parse comment
                            comment_params = parse_comment(comment.body)

                            if comment_params['rating'] is not False:

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
                                    body=comment_params['comment'],
                                    upvotes=comment.score,
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
                                editedComment = update_comment(comment.body)
                                db.session.query(Comment)\
                                    .filter_by(reddit_id=comment.id)\
                                    .update({
                                        "body": editedComment,
                                        "edited_stamp": comment.edited
                                    })
                                db.session.commit()

                        if comment.score != this_comment.upvotes:
                            this_comment.upvotes = comment.score
                            db.session.commit()

            # update last_crawl and reddit score for thread
            thread.last_crawl = datetime.datetime.now()
            if thread.upvotes != submission.score:
                thread.upvotes = submission.score
            db.session.commit()

            # update results on reddit
            if submission.selftext and thread.get_comment_count() != '0':
                results_label_pos = submission.selftext.lower().find(
                    '**live results**'
                )
                if results_label_pos > 0:
                    results_start_pos = submission.selftext.lower()\
                        .find('--', results_label_pos)
                    results_end_pos = submission.selftext.lower()\
                        .find('--', results_start_pos + 1)
                    results_string = \
                        submission.selftext[
                            results_start_pos + 3:results_end_pos
                        ]
                    new_comment_cnt = thread.get_comment_count()
                    if new_comment_cnt == '1':
                        comment_cnt_suffix = 'rating'
                    else:
                        comment_cnt_suffix = 'ratings'
                    new_avg_rating = thread.get_avg_rating()
                    new_reddit_body = submission.selftext.replace(
                        results_string,
                        ' ' + new_avg_rating +
                        ' out of 10, based on ' +
                        new_comment_cnt + ' ' + comment_cnt_suffix + ' '
                    )
                    submission.edit(new_reddit_body)

                else:
                    thread.open_for_comments = False
                    db.session.commit()

            elif submission.selftext is None:
                thread.open_for_comments = False
                db.session.commit()

            # close thread if expired
            if thread.date_posted < \
                    (datetime.datetime.utcnow() -
                     datetime.timedelta(seconds=int(expire))):
                new_selftext = '**Edit:** This thread has been ' + \
                    ' closed. Thanks for participating!\n\n' + \
                    submission.selftext
                submission.edit(new_selftext)
                thread.open_for_comments = False
                db.session.commit()
