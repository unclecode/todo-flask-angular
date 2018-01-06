from flask_limiter import Limiter
from flask import request
from flask_login import current_user


def limiter_host_scope(endpoint_name):
    return request.host
def limiter_key_function():
    return current_user.session_token if current_user and hasattr(current_user, 'session_token') else ''

limiters = {}
def build_limiter(name, app):
    global limiters
    if name in limiters:
        return limiters[name]
    limiter = Limiter(app, key_func=limiter_key_function)
    limiters[name] = limiter
    return limiter

def get_shared_limit(name, app, limit_string):
    global limiters
    limiter = build_limiter(name, app)
    return limiter.shared_limit(
        limit_string,
        limiter_host_scope,
        key_func=limiter_key_function,
        error_message='Exceeds your api limit!'
    )

