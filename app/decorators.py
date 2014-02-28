from flask import flash, session, redirect, url_for
from functools import wraps


# login required wrapper
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('Please login.')
            return redirect(url_for('login'))
    return wrap
