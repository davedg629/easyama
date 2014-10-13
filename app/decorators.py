from flask import abort
from functools import wraps
from flask.ext.login import current_user


# login required wrapper
def admin_login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if current_user.role_id is 1:
            return test(*args, **kwargs)
        else:
            abort(404)
    return wrap
