__author__ = 'unclecode'

import os

class Config():
    # Statement for enabling the development environment
    DEBUG = False
    EXE_MODE = 'proc'

    # Define the application directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    HOST = os.environ.get('WWWHOST', os.environ.get('IP', "0.0.0.0"))
    PORT = os.environ.get('WWWPORT', os.environ.get('PORT', 5050))
    STATIC_FOLDER = "static"
    THREADED=True
    CONFIG_MOD = 'MAIN SERVER'
    SERVER_ADDRESS = "http://ktrial.kidocode.com/"
    LOGS_FOLDER = os.path.dirname(__file__) + '/app/.log'
    if not os.path.exists(LOGS_FOLDER):
        os.mkdir(LOGS_FOLDER)
    TEMPLATE_FOLDER = os.path.dirname(__file__) + '/app/templates'
    IMG_REPO_FOLDER = os.path.dirname(__file__) + '/app/.repo/images/'

    # Define the database - we are working with
    # SQLite for this example
    import json
    try:
        config_data = json.loads(open('../key.txt').read())
    except:
        config_data = {}
        pass
    DATABASES = {
        'mongo': {
            'auth': True,
            'dbname': os.environ.get('DBNAME', config_data.get('DBNAME', '')),
            'url': os.environ.get('DBCONSTR', config_data.get('DBCONSTR', '')),
        },
        'redis': {
            'url': os.environ.get('REDISURL', 'redisToGOURL')
        }
    }
    DATABASE_CONNECT_OPTIONS = {}

    # AWS
    AWS_ID = 'AKIAJWPDVHDFFFALMAJQ'
    AWS_KEY = os.environ.get('AWS_KEY', config_data.get('AWS_KEY', ''))
    AWS_END_POINT_STATIC = ""
    S3_AWS_ID = os.environ.get('S3_KEY_ID', config_data.get('S3_KEY_ID', ''))
    S3_AWS_KEY = os.environ.get('S3_ACESS_KEY', config_data.get('S3_ACESS_KEY', ''))

    # EMAILS
    EMAILS = {
        'info': {
            'smtp': (config_data.get('smtp', ''), config_data.get('smtp_port', 0)),
            'auth': (config_data.get('email', ''), os.environ.get('EMAIL_PASS', config_data.get('email_pass', '')))

        }
    }


    # Application threads. A common general assumption is
    # using 2 per available processor cores - to handle
    # incoming requests using one and performing background
    # operations using the other.
    THREADS_PER_PAGE = 2

    # Enable protection agains *Cross-site Request Forgery (CSRF)*
    CSRF_ENABLED = True

    # Use a secure, unique and absolutely secret key for
    # signing the data.
    CSRF_SESSION_KEY = config_data.get('CSRF', 'unique id')

    # Secret key for signing cookies
    SECRET_KEY = config_data.get('SESSION', 'unique_session_id')


class LocalDev(Config):
    DEBUG = True
    EXE_MODE = 'dev'
    PORT = 8081
    HOST = '0.0.0.0'
    CONFIG_MOD = 'Dev Local Development {0}:{1}/'.format(HOST, str(PORT))
    SERVER_ADDRESS = 'http://{0}:{1}/'.format(HOST, str(PORT))
