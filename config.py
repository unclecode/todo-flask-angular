__author__ = 'unclecode'

import os

class Config():
    # Statement for enabling the development environment
    DEBUG = False
    EXE_MODE = 'proc'

    # Define the application directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    HOST = os.environ.get('WWWHOST', os.environ.get('IP', "0.0.0.0"))
    PORT = int(os.environ.get('WWWPORT', os.environ.get('PORT', 5050)))
    STATIC_FOLDER = "statics"
    THREADED=True
    CONFIG_NAME = "Default"
    CONFIG_MOD = '{0} Config at {1}:{2}/'.format(CONFIG_NAME, HOST, str(PORT))
    SERVER_ADDRESS = "http://fos.kidocode.com/"
    LOGS_FOLDER = BASE_DIR + '/app/.log'
    if not os.path.exists(LOGS_FOLDER):
        os.mkdir(LOGS_FOLDER)
    TEMPLATE_FOLDER = BASE_DIR + '/templates'

    # Define the database - we are working with
    import json
    try:
        config_data = json.loads(open('key.txt').read())
    except:
        config_data = {}
        pass
    DATABASES = {
        'mongo': {
            'auth': True,
            'dbname': os.environ.get('DBNAME', config_data.get('DBNAME', 'YOURDBNAME')),
            'url': os.environ.get('DBCONSTR', config_data.get('DBCONSTR', '')),
        },
        'redis': {
            'url': os.environ.get('REDISURL', 'redisToGOURL')
        }
    }
    DATABASE_CONNECT_OPTIONS = {}
    TEMPLATES_AUTO_RELOAD = False

    # AWS
    AWS_ID = os.environ.get('AWS_ID', config_data.get('AWS_ID', ''))
    AWS_KEY = os.environ.get('AWS_KEY', config_data.get('AWS_KEY', ''))
    AWS_END_POINT_STATIC = ""
    S3_AWS_ID = os.environ.get('S3_KEY_ID', config_data.get('S3_KEY_ID', ''))
    S3_AWS_KEY = os.environ.get('S3_ACCESS_KEY', config_data.get('S3_ACCESS_KEY', ''))

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
    # THREADS_PER_PAGE = 2

    # Enable protection agains *Cross-site Request Forgery (CSRF)*
    CSRF_ENABLED = True

    # Use a secure, unique and absolutely secret key for
    # signing the data.
    CSRF_SESSION_KEY = config_data.get('CSRF', '145a6adc782a11e7a5c4985aebdbba9e')

    # Secret key for signing cookies
    SECRET_KEY = config_data.get('SESSION', '1f08bb78782a11e7b7a0985aebdbba9e')

    def getConfigMode(self):
        return '{0} at {1}:{2}/'.format(Config.CONFIG_NAME, Config.HOST, str(Config.PORT))


class LocalDev(Config):
    DEBUG = True
    EXE_MODE = 'dev'
    PORT = 8080
    HOST = '0.0.0.0'
    CONFIG_NAME = "Development Server"
    CONFIG_MOD = '{0} at {1}:{2}/'.format(CONFIG_NAME, HOST, str(PORT))
    SERVER_ADDRESS = 'http://{0}:{1}/'.format(HOST, str(PORT))
    TEMPLATES_AUTO_RELOAD = True
