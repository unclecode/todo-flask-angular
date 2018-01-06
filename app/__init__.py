__author__ = 'unclecode'
from flask import Flask, render_template, session, make_response, request
from flask_socketio import SocketIO
from flask_session import Session
from flask_restful import Resource, Api
from flask_mongoengine import MongoEngine, BaseQuerySet
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from flask_login import LoginManager, current_user
from flask_cache import Cache
from flask_mail import Mail

import os, pymongo, datetime, time

app = Flask(os.environ.get('APPNAME', 'KTodo'), static_folder='statics')

# Flask-HTTPAuth Configurations
basicAuth = HTTPBasicAuth()
tokenAuth = HTTPTokenAuth(scheme="token")

# Flask-Login
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.init_app(app)

#Flask-Limitter
app.config['RATELIMIT_HEADERS_ENABLED'] = True
app.config['RATELIMIT_ENABLED'] = True

# Flask-Cache
cache = Cache(config={
    'CACHE_TYPE': 'simple', #null, simple, redis, filesystem
    'CACHE_DEFAULT_TIMEOUT': 10
})
# cache.init_app(app)

# Configurations
app.config.from_object('config.' + os.environ.get('CONFIG_MOD', 'LocalDev'))

# set the secret key.  keep this really secret:
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(hours=1)
from app.lib.mongoFlaskSession import *
app.session_interface = MongoSessionInterface(db=app.config['DATABASES']['dbname'])
Session().init_app(app)
api = Api(app)

mail = Mail()
mail.init_app(app)

print " * Connecting to MongoDB & Redis"
# Define the database object which is imported by modules and controllers

mongodb = pymongo.MongoClient(app.config['DATABASES']['url'] or None)[app.config['DATABASES']['dbname']]
db = MongoEngine(app)

app.jinja_env.globals.update(session=session)
@app.template_filter('ctime')
def timectime(s):
    return time.ctime(s) # datetime.datetime.fromtimestamp(s)

@app.template_filter('cdelta')
def timedelta(s):
    hr = s / 3600
    mn = (s % 3600) / 60
    sn = (s % 3600) % 60
    return "{0}:{1:02d}:{2:02d}".format(int(hr), int(mn), int(sn))

@app.errorhandler(403)
def not_found(error):
    return render_template('error/403.html'), 403

@app.errorhandler(404)
def not_found(error):
    return render_template('error/404.html'), 404

@app.errorhandler(400)
def not_found(error):
    return render_template('error/400.html'), 400

@app.errorhandler(500)
def server_error(error):
    # app.logger.exception(error)
    return render_template('error/500.html'), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return make_response(jsonify(error="api rate limit exceeded %s" % e.description), 429)

from app.modules.index import mod_index
from app.modules.api.v1.users import api_user
from app.modules.api.v1.tasks import api_task
from app.modules.api.v1.notes import api_task_note
from app.modules.auth import *
from modules.users import mod_users

# Register blueprint(s)
routes = [
    ('/', mod_index),
    ('/api/v1/users', api_user),
    ('/api/v1/tasks', api_task),
    ('/api/v1/tasks/notes', api_task_note),
    ('/users', mod_users),
    ('/auth', mod_auth)
]

for route in routes:
    app.register_blueprint(route[1], url_prefix=route[0])

socketio = SocketIO()
socketio.init_app(app)

if app.config['USE_FLASK_ASSETS']:
    from flask_assets import Environment, Bundle
    from webassets.loaders import YAMLLoader
    assets = Environment(app)
    assets.from_yaml( app.config['BASE_DIR'] + '/assets.yaml')

if app.config['REFRESH_FLASK_S3']:
    from flask_s3 import FlaskS3, create_all
    s3 = FlaskS3(app)
    create_all(app)
    #create_all(app, filepath_filter_regex = "^out")
    #create_all(app,               user="AKIAIJ7GI62JML4A3G6Q",               password = "Ae/Y/t7UYOk/cSunSPkpQo9erFXdG05+1BRqAha7",               bucket_name= "unclecode.test.assets",               location="ap-southeast-1")

