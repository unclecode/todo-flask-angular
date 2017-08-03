__author__ = 'unclecode'
from flask import Flask, render_template, session
from flask_socketio import SocketIO
from flask_session import Session

import os, pymongo, datetime, time

app = Flask(os.environ.get('APPNAME', '<APPNAME>'), static_folder='statics')

# Configurations
app.config.from_object('config.' + os.environ.get('CONFIG_MOD', 'LocalDev'))

# set the secret key.  keep this really secret:
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(hours=1)
Session().init_app(app)

print " * Connecting to MongoDB & Redis"
# Define the database object which is imported by modules and controllers
mongodb = pymongo.MongoClient(app.config['DATABASES']['mongo']['url'] or None)[app.config['DATABASES']['mongo']['dbname']]

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


from app.modules.index.controller import mod_index

# Register blueprint(s)
routes = [
    ('/', mod_index),
]

for route in routes:
    app.register_blueprint(route[1], url_prefix=route[0])


socketio = SocketIO()
socketio.init_app(app)
