import sys
if 'threading' in sys.modules:
    del sys.modules['threading']

import gevent
import gevent.socket
import gevent.monkey
from gevent.wsgi import WSGIServer
gevent.monkey.patch_all()

from werkzeug.serving import run_with_reloader

from app import app, socketio

# @socketio.on('connect')
# def connect():
#     print('Connected')
#
# @socketio.on('test')
# def test():
#     emit('listen', {'d':'hello'}, broadcast=True)

@run_with_reloader
def run_server():
    print(' * start server at: http://%s:%s - mode : %s - config : %s' % (
        app.config['HOST'], app.config['PORT'],
        app.config['EXE_MODE'],
        app.config['CONFIG_MOD']))

    # import logging
    # logging.basicConfig(filename='../logs/kportal/error.log', level=logging.DEBUG)

    #run using socketio
    #socketio.run(app, host = app.config['HOST'], port = app.config['PORT']) #, debug=True,threaded=True)

    #Run with flask
    #app.run(host = app.config['HOST'], port = app.config['PORT'], debug=True, threaded=True)
    #print "Run speech server on " + str(sysProfile['SPEECHSERVERPORT'])

    #run async usign gevent
    app.debug = True
    http_server = WSGIServer((app.config['HOST'], app.config['PORT']), app)
    http_server.serve_forever()

if __name__ == "__main__":
    run_server()
