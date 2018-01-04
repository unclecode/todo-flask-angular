__author__ = 'unclecode'

# Using flask-limiter
# Helpers: GeoIP
# https://flask-limiter.readthedocs.io/en/stable/

import sys, os, json, hashlib, uuid, base64, random
if '/Library/Python/2.7/site-packages' not in sys.path:
    sys.path.insert(0, '/Library/Python/2.7/site-packages')
from flask import Flask, make_response, redirect, request, url_for, Response, current_app, g, jsonify, views

from flask_limiter import Limiter, HEADERS
from flask_limiter.util import get_ipaddr, get_remote_address

from geoip import geolite2, open_database

app = Flask(__name__)
app.config['CUSTOM_LIMIT'] = "1/second"
"""
Apply limiter to whole app!
Using of decorator to override the global limits
Using decorator to exempt from one of the end point
Use customer rate limit function
Use custom exempt function
Shared limit
Create White list! No limit for all requests coming from specific IP our VIP account
Configurations
:return:
"""
# Default rate limit will be applied to all routes if nothing specify, of course if you define default_limits
# in constructor then it's okay!
# app.config['RATELIMIT_DEFAULT'] = "10/second"

# To have reate limit details in response headers
# A Sample"
# Content-Type: text/html
# Content-Length: 139
# X-RateLimit-Limit: 1
# X-RateLimit-Remaining: 0
# X-RateLimit-Reset: 1503815033
# Retry-After: 86375
# Server: Werkzeug/0.12.2 Python/2.7.13
# Date: Sat, 26 Aug 2017 06:24:17 GMT
app.config['RATELIMIT_HEADERS_ENABLED'] = True
# These three headers can be customized, by assigning values to RATELIMIT_HEADER_LIMIT, RATELIMIT_HEADER_RESET, RATELIMIT_HEADER_REMAINING

# To stop whole rate limit
app.config['RATELIMIT_ENABLED'] = True

# Whether to allow failures while attempting to perform a rate limit such as errors with downstream storage
app.config['RATELIMIT_SWALLOW_ERRORS'] = True

# Three strategies to limit the rate
# https://flask-limiter.readthedocs.io/en/stable/#ratelimit-strategy
app.config['RATELIMIT_STRATEGY'] = "fixed-window-elastic-expiry" # fixed-window, or fixed-window-elastic-expiry, or moving-window

limiter = Limiter(
    app,
    key_func=get_remote_address, # It's better to be one of our function that return a unique string like user access token, or user id or api key! Better than  IP
    default_limits=["200 per day", "50 per hour"]
)
"""String Format for limit:
    [count] [per|/] [n (optional)] [second|minute|hour|day|month|year]

    EXAMPLE
        10 per hour
        10/hour
        10/hour;100/day;2000 per year
        100/day, 500/7days
"""


# Headers name can be customized
limiter.header_mapping = {
    HEADERS.LIMIT : "X-My-Limit",
    HEADERS.RESET : "X-My-Reset",
    HEADERS.REMAINING: "X-My-Remaining"
}


def rate_limit_from_config():
    return current_app.config.get("CUSTOM_LIMIT", "10/second")



@app.route("/slow/0")
@limiter.limit("1/day", error_message='chill!')
def slow0():
    return "24"

@app.route("/slow")
@limiter.limit("1 per day")
def slow():
    return "24"

@app.route("/slow/2")
@limiter.limit("100/day;20/hour;10/minute;1/second") # This is very good way of limiting! If you say only 100 a day, then a hacker wait 11:59 and send 100 and 00:01 send another 100!
def slow2():
    return "24"

@app.route("/slow/3")
@limiter.limit(rate_limit_from_config)
def slow3():
    return "24"

current_user = {
    'is_admin': True,
    'id':'unclecode'
}

@app.route("/slow/4")
@limiter.limit("100/day;1/second", exempt_when=lambda: current_user['is_admin'])
def slow4():
    return "24"

def host_scope(endpoint_name):
    return request.host

api_shared_limit = limiter.shared_limit("10/minute", scope=host_scope) # it can be just a simple string name

@app.route("/slow/5/1")
@api_shared_limit
def slow51():
    return "24"

@app.route("/slow/5/2")
@api_shared_limit
def slow52():
    return "24"

def get_user_id():
    return current_user['id']

@app.route("/slow/6")
@limiter.limit("2 per day", key_func = get_user_id)
def slow6():
    return "24"

myLoc = None
def get_request_country():
    global myLoc
    if not any(x for x in ['local', '192', '127'] if request.remote_addr[:5].startswith(x)):
        match = geolite2.lookup(request.remote_addr)
    else:
        if not myLoc:
            match = myLoc = geolite2.lookup_mine()
        else:
            match = myLoc

    return match.country


# Using custom Key_func! This can check api_key of current user or other citeria
@app.route("/slow/7")
@limiter.limit("2 per day", key_func = get_request_country)
def slow7():
    return "24"

@app.route("/fast")
def fast():
    return "42"

@app.route("/ping")
@limiter.exempt
def ping():
    return "PONG"

# Samples of white list
@limiter.request_filter
def header_whitelist():
    #return request.headers.get("X-Internal", "") == "true"
    return False

@limiter.request_filter
def ip_whitelist():
    #return request.remote_addr == "127.0.0.1"
    return False

@app.errorhandler(429)
def ratelimit_handler(e):
    return make_response(
            jsonify(error="ratelimit exceeded %s" % e.description)
            , 429
    )


class MyView(views.MethodView):
    decorators = [limiter.limit("5/day")] # Or use per token or api+key or user id using
    def get(self):
        return "get"

    def put(self):
        return "put"

app.add_url_rule("/data", view_func=MyView.as_view('data'))

# Using limiter with blue prints:
# Limiter.limit(), Limiter.shared_limit() & Limiter.exempt() can all be applied to
# flask.Blueprint instances as well. In the following example the login Blueprint
# has a special rate limit applied to all its routes, while the help Blueprint is
# exempt from all rate limits. The regular Blueprint follows the default rate limits.

# app = Flask(__name__)
# login = Blueprint("login", __name__, url_prefix = "/login")
# regular = Blueprint("regular", __name__, url_prefix = "/regular")
# doc = Blueprint("doc", __name__, url_prefix = "/doc")
#
# @doc.route("/")
# def doc_index():
#     return "doc"
#
# @regular.route("/")
# def regular_index():
#     return "regular"
#
# @login.route("/")
# def login_index():
#     return "login"
#
# limiter = Limiter(app, default_limits = ["1/second"], key_func=get_remote_address)
# limiter.limit("60/hour")(login)
# limiter.exempt(doc)
#
# app.register_blueprint(doc)
# app.register_blueprint(login)
# app.register_blueprint(regular)

if __name__ == "__main__":
    app.run(debug=True)