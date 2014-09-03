import os

basedir = os.path.abspath(os.path.dirname(__file__))

CSRF_ENABLED = True
DEBUG = True

# set to 'heroku' if hosting with heroku
if os.environ.get('ENVIRONMENT') is None:
    ENVIRONMENT = 'dev'
else:
    ENVIRONMENT = os.environ.get('ENVIRONMENT')

# server name
if os.environ.get('SERVER_NAME') is None:
    SERVER_NAME = 'localhost:5000'
else:
    SERVER_NAME = os.environ.get('SERVER_NAME')

# naked server name, set to example.com if ENVIROMENT is set to 'heroku'
if os.environ.get('NAKED_SERVER_NAME') is None:
    NAKED_SERVER_NAME = 'localhost:5000'
else:
    NAKED_SERVER_NAME = os.environ.get('NAKED_SERVER_NAME')

# flask secret key
if os.environ.get('SECRET_KEY') is None:
    SECRET_KEY = 'a_really_good_secret_key'
else:
    SECRET_KEY = os.environ.get('SECRET_KEY')

# SQLALchemy database URI
if os.environ.get('DATABASE_URL') is None:
    DATABASE = 'amapro.db'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
        os.path.join(basedir, DATABASE) + \
        '?check_same_thread=False'
else:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

# Google Analytics
if os.environ.get('GA_TRACKING_ID') is None:
    GA_TRACKING_ID = 'UA-XXXXXXXX-XX'
else:
    GA_TRACKING_ID = os.environ.get('GA_TRACKING_ID')

if os.environ.get('GA_DEFAULT_URL') is None:
    GA_DEFAULT_URL = 'your-domain.com'
else:
    GA_DEFAULT_URL = os.environ.get('GA_DEFAULT_URL')

# favicon url
if os.environ.get('FAVICON_URL') is None:
    FAVICON_URL = 'favicon_url_here'
else:
    FAVICON_URL = os.environ.get('FAVICON_URL')
