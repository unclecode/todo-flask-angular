__author__ = 'unclecode'

# Usinf flask-cache
# https://pythonhosted.org/Flask-Cache

import sys, os, json, hashlib, uuid, base64, random
if '/Library/Python/2.7/site-packages' not in sys.path:
    sys.path.insert(0, '/Library/Python/2.7/site-packages')
from flask import Flask, make_response, redirect, request, url_for, Response, current_app, g, jsonify, views

from flask_cache import Cache

app = Flask(__name__)

cache = Cache(config={
    'CACHE_TYPE': 'simple', #null, simple, redis, filesystem
    'CACHE_DEFAULT_TIMEOUT': 10
    # CACHE_REDIS_URL URL to connect to Redis server. Example redis://user:password@localhost:6379/2. Used only for RedisCache.
    # CACHE_REDIS_HOST
    # CACHE_REDIS_PORT
    # CACHE_REDIS_PASSWORD
    # CACHE_REDIS_DB  default is 0
    # CACHE_DIR only for filesystem mode
})
cache.init_app(app)


data = "hello"
c = 0


def should_by_pass_chached():
    """
    If retuens True then caching will be bypassed, so a function to indicate should i by pass or not
    :return:
    """
    global c, data
    d = data
    c = (c % 5) + 1
    if c % 5 == 0:
        d = str(uuid.uuid1())
    if d != data:
        data = d
        print c, d, data
        return True
    print c, d, data
    return False


# You can cache a function result but key_prefix must be given to dintinguish from default that look at request.path
@cache.cached(timeout=10, key_prefix='all_comments')
def get_all_comments():
    comments = [random.choice(range(100)) for _ in range(10)]
    return str(comments)

# Test it in console using ...    with app.app_context() as ctx: get_all_comments()



@app.route('/')
@cache.cached(timeout=10)
def index():
    return str(random.choice(range(100))) + '\n\r'

# When unless returns True, then index2() will be executed, but if it returns True in next round and still cache time is not expired thenthe last cached result will be returnes
@app.route('/2')
@cache.cached(timeout=50, unless=should_by_pass_chached)
def index2():
    return str(random.choice(range(100))) + '\n\r'

# Memorize a function result for the given specific parameters! So a function without parameters reacts same way if you use cache or memize
@app.route('/3/<int:x>')
@cache.memoize(timeout=20, make_name="index3")
def index3(x):
    return str(random.choice(range(x))) + '\n\r'

@app.route('/4')
@cache.memoize(timeout=50, unless=should_by_pass_chached)
def index4():
    return str(random.choice(range(100))) + '\n\r'

@app.route('/5')
def index5():
    cache.delete_memoized(index4)
    return 'done\n\r'

@app.route('/6/<int:x>')
def index6(x):
    cache.delete_memoized(index3, x)
    return 'done\n\r'

@app.route('/7')
def index7():
    cache.clear()
    return 'done\n\r'

@app.route('/8')
@cache.cached() #usinf default time out
def index8():
    return str(random.choice(range(100))) + '\n\r'



if __name__ == "__main__":
    app.run(debug=True)
