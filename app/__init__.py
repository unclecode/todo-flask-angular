__author__ = 'unclecode'
from flask import Flask, render_template, session
from flask_socketio import SocketIO
from flask_session import Session

import os, pymongo, datetime, time

app = Flask('ktrial', static_folder='statics')

# Configurations
app.config.from_object('config.' + os.environ.get('KIDO_CONFIG_MOD', 'LocalDev'))

# set the secret key.  keep this really secret:
app.secret_key = '170bef4f-4ff8-11e5-b346-005056'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(hours=1)
Session().init_app(app)

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

app.config['TEMPLATES_AUTO_RELOAD'] = True

# The amount of time after which the user's session expires
# (this is a Flask setting and is also used by the Javascript)
app.permanent_session_lifetime = datetime.timedelta(hours=1)

ROOT_PATH = os.getcwd()

if app.config['DATABASES']['mongo']['url']:
    print " * Connecting to MongoDB & Redis"
    # Define the database object which is imported by modules and controllers
    mongodb = pymongo.MongoClient(app.config['DATABASES']['mongo']['url'])[app.config['DATABASES']['mongo']['dbname']]

    ip_urls = ["http://ipinfo.io", ROOT_PATH + "/data/allowed_ip.json"]

    # MongoDB INDEXES
    db_params = {
        'members_count': 0  # mongodb.members.find({}, {'_id':1}).count()
    }

socketio = SocketIO()


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(error):
    # app.logger.exception(error)
    return render_template('500.html'), 500


from app.modules.index.controller import mod_index

# Register blueprint(s)
routes = [
    ('/', mod_index),
]

for route in routes:
    app.register_blueprint(route[1], url_prefix=route[0])


# Context Processor
# Convert linux time to normal time (h/m/s)
@app.context_processor
def change_time_format_processor():
    def format_time(linux_time):
        try:
            return time.strftime('%H:%M:%S', time.gmtime(linux_time))
        except Exception as ex:
            print(ex.message)
            return "-"

    return dict(format_time=format_time)


# Context Processor
# Convert linux time to normal date (dd/mm/yyyy)
@app.context_processor
def change_date_format_processor():
    def format_date(linux_time):
        try:
            return datetime.datetime.fromtimestamp(int(linux_time) + 28800).strftime('%H:%M:%S | %d/%m/%Y ')
        except Exception as ex:
            print(ex.message)
            return "-"

    return dict(format_date=format_date)


@app.context_processor
def add_session_config():
    return {
        'PERMANENT_SESSION_LIFETIME_MS': (app.permanent_session_lifetime.seconds * 1000),
    }


socketio.init_app(app)
