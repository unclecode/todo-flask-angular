__author__ = 'unclecode'

# SocketIO Extiension


import sys, os, json, hashlib, uuid, base64, random, functools, time, threading
from threading import Thread
if '/Library/Python/2.7/site-packages' not in sys.path:
    sys.path.insert(0, '/Library/Python/2.7/site-packages')

from flask import Flask, make_response, redirect, request,\
    url_for, Response, current_app, g, jsonify, views, \
    render_template_string, session, render_template

from flask_login import current_user


# import gevent
# import gevent.socket
# import gevent.monkey
# from gevent.wsgi import WSGIServer
# gevent.monkey.patch_all()

# About Seesion: Main HTTP Session is available only as readonly, but its available! Socketio handler that
# their own session whicch has read/write access, and as mentioned it can read http session
# focus on how to combine socket io with flask-login
# In this case Socketio has access to current_user from flask-login and can check current_user.is_authenticated
# can't use @login_required but you can make your own decorator


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            return {'result':False}, 400
        else:
            return f(*args, **kwargs)
    return wrapped


from flask_session import Session
from flask_socketio import SocketIO, send, emit, join_room, leave_room


app = Flask(__name__)
app.debug = True
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = "WOWOWOWOW"
Session().init_app(app)

socketio = SocketIO(app)

import redis
r = redis.StrictRedis(host='localhost', port=6379, db=0)
pb = r.pubsub()
pb.subscribe("socketio")

# def dispatch():
#     print "redis..."
#     while True:
#         message = pb.get_message()
#         if message:
#             d = r.hgetall("socketio")
#             if d and d.get('action', '') == 'share':
#                 with app.app_context() as ctx:
#                     r.delete("socketio")
#                     socketio.emit("get", "data from redis")
#                 print d
#         time.sleep(0.001)

dispatch_thread = Thread()
thread_stop_event = threading.Event()

class RedisReadThread(Thread):
    def __init__(self):
        self.delay = 0.001
        super(RedisReadThread, self).__init__()

    def read(self):
        """
        Generate a random number every 1 second and emit to a socketio instance (broadcast)
        Ideally to be run in a separate thread?
        """
        #infinite loop of magical random numbers
        print "Redis..."
        while not thread_stop_event.isSet():
            message = pb.get_message()
            if message:
                d = r.hgetall("socketio")
                if d and d.get('action', '') == 'share':
                    with app.app_context() as ctx:
                        r.delete("socketio")
                        socketio.emit("get", "data from redis", namespace="/stream")
                    print d
            time.sleep(self.delay)

    def run(self):
        self.read()


@app.route('/')
def index():
    return 'running'


@socketio.on('connect')
def test_connect1():
    global dispatch_thread
    print "%s - %s connected" % (request.namespace, request.sid)
    # we make onr room with the name of socketio seesion id to have individual communication
    join_room(request.sid)
    session['x'] = 5
    emit('/ response', {'data': 'Connected'})

@socketio.on('disconnect')
def test_connect1():
    leave_room(request.sid)
    print "%s - %s disconnected" % (request.namespace, request.sid)
    print "/ disconnected"

# for every namespave you can define a connect event, and actually in client side you must connect
# to every namespace, otherwise the defualt name space in client side can't listen to messages coming
@socketio.on('connect', namespace='/db')
def test_connect2():
    print "%s - %s connected" % (request.namespace, request.sid)
    emit('/db response', {'data': 'Connected'})


@socketio.on('connect', namespace='/stream')
def test_connect3():
    global dispatch_thread
    print "%s - %s connected" % (request.namespace, request.sid)
    emit('/stream response', {'data': 'Connected'})
    if not dispatch_thread.isAlive():
        dispatch_thread = RedisReadThread()
        dispatch_thread.start()


def ack():
    print "Yay!"

@app.route('/2')
def index2():
    session['me'] = "hello"
    return "hi"

@app.route('/3')
def index3():
    socketio.emit("helloooooo")
    socketio.emit("helloooooo", namespace="/db")
    return "hi"

@socketio.on('event')
def my_event(json):
    # x, y are only socket session, me is overriding but in http side still is HELLO
    session['y'] = 4
    session['x'] = 4
    session['me'] = "hi"

    print "received json: " + str(json)
    send("event", callback=ack) #You can skip namespace as if not provided it will use default one
    emit("get", {'d':4}, namespace="/")
    return {'res':'/'}, 10 # send back multiple parameters

@socketio.on('event', namespace="/db")
def my_event1(json):
    print "received DB json: " + str(json)
    send("eventDB")
    send({"d":"json-db"}, namespace="/db", callback=ack)
    return {'res':'db'}, 20 # send back multiple parameters

@socketio.on('event', namespace="/stream")
def my_event2(json):
    print "received STREAM json: " + str(json)
    send({'d':'json-stream'}, json=True)
    return {'res':'stream'}, 30 # send back multiple parameters

@socketio.on('event1')
def my_event3(a, b, c):
    print "received params: " + str(a) + str(b) + str(c)
    send({'d':'json-stream'}, json=True)
    return {'res':True}, 10 # send back multiple parameters

@socketio.on('all')
def handle_my_custom_event(data):
    print "all " + str(data)
    send("all")
    emit('hello all', data, broadcast=True)
    return {'count':10}, 10

@socketio.on('join')
def join(data):
    join_room(data['id'] + ':' + request.sid)
    return {'count':10}, 10

@socketio.on('leave')
def leave(data):
    leave_room(data['id'] + ':' + request.sid)
    return {'count':10}, 10

@socketio.on('one')
def one_send(data):
    send("all")
    send('hellozz', room=request.sid)
    return {'count':10}, 10

@socketio.on_error()        # Handles the default namespace
def error_handler(e):
    print "error " + str(e)
    pass

@socketio.on_error('/db') # handles the '/chat' namespace
def error_handler_chat(e):
    print "error " + str(e)
    pass

@socketio.on_error('/stream') # handles the '/chat' namespace
def error_handler_chat(e):
    print "error " + str(e)
    pass

@socketio.on_error_default  # handles all namespaces without an explicit error handler
def default_error_handler(e):
    print "error general " + str(e)
    print(request.event["message"]) # "my error event"
    print(request.event["args"])    # (data,)
    pass





# from werkzeug.serving import run_with_reloader
#
# from app import app
#
# @run_with_reloader
# def run_server():
#     global app
#     print(' * start server at: http://%s:%s - mode : %s - config : %s - Debug %s' % (
#         app.config['HOST'], app.config['PORT'],
#         app.config['EXE_MODE'],
#         app.config['CONFIG_MOD'],
#         app.config['DEBUG']))
#     # app.run(host = app.config['HOST'], port = app.config['PORT'])
#     http_server = WSGIServer((app.config['HOST'], app.config['PORT']), socketio)
#     http_server.serve_forever()
#
# if __name__ == "__main__":
#     run_server()
#
#
if __name__ == "__main__":
    #app.run(port=5001, debug = False)
    socketio.run(app, port=5001, debug = False)
