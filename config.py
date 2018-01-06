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
    #EXPLAIN_TEMPLATE_LOADING = True
    THREADED=True
    CONFIG_NAME = "Default"
    CONFIG_MOD = '{0} Config at {1}:{2}/'.format(CONFIG_NAME, HOST, str(PORT))
    SERVER_ADDRESS = "http://{0}:{1}/".format(HOST, str(PORT))
    LOGS_FOLDER = BASE_DIR + '/app/.log'
    if not os.path.exists(LOGS_FOLDER):
        os.mkdir(LOGS_FOLDER)
    TEMPLATE_FOLDER = BASE_DIR + '/templates'

    # Define the database - we are working with
    import json
    config_data = json.loads(open( BASE_DIR + '/key.json').read())

    DATABASES = {
        'dbname': os.environ.get('DBNAME', config_data.get('DBNAME', 'YOURDBNAME')),
        'url': os.environ.get('DBCONSTR', config_data.get('DBCONSTR', '')),
    }

    # MongoEngine Settings
    MONGODB_DB = os.environ.get('DBNAME', config_data.get('DBNAME', 'YOURDBNAME'))
    MONGODB_HOST = os.environ.get('DBCONSTR', config_data.get('DBCONSTR', 'mongodb://localhost/' + MONGODB_DB))

    # flak-mail
    MAIL_SERVER = "SMTP.GMAIL.COM"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = "DidIt Assistant"
    MAIL_DEBUG = False
    # MAIL_MAX_EMAILS for those mailserver that have limit for number of emails you can send in one open connection


    # S3 Bucket
    USE_FLASK_S3 = True
    REFRESH_FLASK_S3 = False
    FLASKS3_BUCKET_NAME = 'unclecode.test.assets'
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
    FLASKS3_REGION = "ap-southeast-1"
    FLASKS3_FORCE_MIMETYPE = True
    FLASKS3_USE_HTTPS = False
    FLASKS3_GZIP = True
    # Indicate if Flask3S should work even when app is running in debug mode
    FLASKS3_DEBUG = True
    FLASKS3_ACTIVE = True

    #Flask Assets
    USE_FLASK_ASSETS = True
    # If flask-assets should work when app is running in debug?
    ASSETS_DEBUG = False
    FLASK_ASSETS_USE_S3 = USE_FLASK_S3

    TEMPLATES_AUTO_RELOAD = False
    THREADS_PER_PAGE = 2
    # Enable protection agains *Cross-site Request Forgery (CSRF)*
    CSRF_ENABLED = True
    # Use a secure, unique and absolutely secret key for
    CSRF_SESSION_KEY = os.environ.get('CSRF', '')
    #CSRF_SESSION_KEY = config_data.get('CSRF', 'e06f08d32ede16d1c911c01b93f7ae79deeaca48db5cb7ed')
    # Secret key for signing cookies
    # Follow this to have good key import os; key = os.urandom(24)
    SECRET_KEY = os.environ.get('SECRET_KEY_COOKIE', '')
    #SECRET_KEY = config_data.get('SECRET_KEY', '7a09ed6bec52ecc6c06039d965e466be85f8bd3e3d87b33b')

    def getConfigMode(self):
        return '{0} at {1}:{2}/'.format(Config.CONFIG_NAME, Config.HOST, str(Config.PORT))


class LocalDev(Config):
    DEBUG = True
    EXE_MODE = 'dev'
    PORT = 9090
    HOST = '0.0.0.0'
    CONFIG_NAME = "Development Server"
    CONFIG_MOD = '{0} at {1}:{2}/'.format(CONFIG_NAME, HOST, str(PORT))
    SERVER_ADDRESS = 'http://{0}:{1}/'.format(HOST, str(PORT))
    TEMPLATES_AUTO_RELOAD = True

class LocalDevOptimized(LocalDev):
    ASSETS_DEBUG = False
    FLASKS3_DEBUG = True
    FLASKS3_ACTIVE = True
    FLASK_ASSETS_USE_S3 = True
    CONFIG_NAME = "Development Server (Asset Optimized, S3)"

class Release(Config):
    DEBUG = False
    ASSETS_DEBUG = False
    EXE_MODE = 'prc'
    PORT = 80
    HOST = '0.0.0.0'
    CONFIG_NAME = "Release Server"
    CONFIG_MOD = '{0} at {1}:{2}/'.format(CONFIG_NAME, HOST, str(PORT))
    SERVER_ADDRESS = 'http://{0}:{1}/'.format(HOST, str(PORT))
    TEMPLATES_AUTO_RELOAD = True
