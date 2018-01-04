import sys

if 'threading' in sys.modules:
    del sys.modules['threading']

import gevent
import gevent.socket
import gevent.monkey
from gevent.wsgi import WSGIServer
gevent.monkey.patch_all()

from werkzeug.serving import run_with_reloader

from app import app

@run_with_reloader
def run_server():
    global app
    print(' * start server at: http://%s:%s - mode : %s - config : %s - Debug %s' % (
        app.config['HOST'], app.config['PORT'],
        app.config['EXE_MODE'],
        app.config['CONFIG_MOD'],
        app.config['DEBUG']))
    # app.run(host = app.config['HOST'], port = app.config['PORT'])
    http_server = WSGIServer((app.config['HOST'], app.config['PORT']), app)
    http_server.serve_forever()

if __name__ == "__main__":
    run_server()
