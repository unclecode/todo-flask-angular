import sys
if 'threading' in sys.modules:
    del sys.modules['threading']
import gevent
import gevent.socket
import gevent.monkey
gevent.monkey.patch_all()

from werkzeug.serving import run_with_reloader
from app import socketio, app

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


    #socketio.run(app, host = app.config['HOST'], port = app.config['PORT']) #, debug=True,threaded=True)
    app.run(host = app.config['HOST'], port = app.config['PORT'], debug=True, threaded=True)


if __name__ == "__main__":
    run_server()
