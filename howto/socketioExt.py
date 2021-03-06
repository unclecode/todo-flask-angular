__author__ = 'unclecode'

# SocketIO Extiension
#

import sys, os, json, hashlib, uuid, base64, random
if '/Library/Python/2.7/site-packages' not in sys.path:
    sys.path.insert(0, '/Library/Python/2.7/site-packages')
from flask import Flask, make_response, redirect, request,\
    url_for, Response, current_app, g, jsonify, views, \
    render_template_string, session, render_template

from flask_session import Session



app = Flask(__name__)
app.debug = True
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = "WOWOWOWOW"
Session().init_app(app)

import redis
r = redis.StrictRedis(host='localhost', port=6379, db=0)
pb = r.pubsub()

@app.route('/')
def index():
    return render_template("socketio.html")

@app.route('/do')
def do():
    # we do some tasks and set the result into redis to make it available for socketio server
    r.hmset("socketio", {"d":"test", "action":"share"})
    r.publish("socketio", "ping")
    return "done"

if __name__ == "__main__":
    app.run(debug = True)
