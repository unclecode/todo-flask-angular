__author__ = 'unclecode'

from functools import update_wrapper, wraps
from flask import make_response

# Use this to avoid standard browser cache
def nocache(f):
    @wraps(f)
    def new_func(*args, **kwargs):
        resp = make_response(f(*args, **kwargs))
        resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0'
        return resp
    return update_wrapper(new_func, f)

