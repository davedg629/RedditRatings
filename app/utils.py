from __future__ import division
from flask import flash
import re
from unicodedata import normalize
from config import SERVER_NAME


# flash errors
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the {} field - {}".format(
                getattr(form, field).label.text,
                error
            ), 'error')


#check if a string is an integer
def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


# turn text into slug
def make_slug(text, delim=u'-'):
    """Generates a slightly worse ASCII-only slug."""
    _punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
    result = []
    for word in _punct_re.split(text.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delim.join(result))


# get time ago from datetime
def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time, datetime):
        diff = now - time
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(second_diff // 60) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(second_diff // 3600) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff // 7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff // 30) + " months ago"
    return str(day_diff // 365) + " years ago"


# construct reddit post body
def reddit_body(desc, title, cat_slug, slug):
    body = (
        desc +
        '\n\n-'
        '\n---'
        '\n-'
        '\n\n**What are we rating?**\n\n' +
        title +
        '\n\n-'
        '\n---'
        '\n-'
        '\n\n**How do I submit a rating?**'
        '\n\nYou can submit a rating by leaving a comment with'
        ' the following format:'
        '\n\n    Rating: Provide a rating from 1 to 10 here, whole numbers'
        ' only, required'
        '\n\n    Comment: Include any comments related to your rating here,'
        ' encouraged but optional'
        '\n\n    ---'
        '\n\n    If you want to say something not directly related to your'
        ' rating, put it\n    below a horizontal rule ("---").'
        '\n\n    verifyrating'
        '\n\n    If the text "verifyrating" is included, then a PM will be'
        ' sent to you\n    when your rating is parsed.'
        '\n\n-'
        '\n---'
        '\n-'
        '\n\n**Then what happens?**'
        '\n\nEvery few minutes, a bot will scan the comments and calculate'
        ' an average rating based on your input.'
        '\n\n-'
        '\n---'
        '\n-'
        '\n\n**Live results**'
        '\n\n[?? out of 10, based on 0 ratings]('
        'http://' + SERVER_NAME +
        '/' + cat_slug + '/' + slug + ')'
        '\n\n*^Updates ^every ^10 ^minutes*'
        '\n\n-'
        '\n---'
        '\n-'
        '\n\n**Helpful tips**'
        '\n\n* Only your first Rating will be counted.'
        '\n* You have 3 minutes to edit your Rating.'
        '\n* Upvote other Ratings that are informative.'
        '\n* Post feedback and suggestions to /r/RedditRatings.')
    return body
