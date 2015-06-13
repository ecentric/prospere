# Django settings for prospere project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('nickolas', 'nickolas.shishov@yandex.ua'),
)

MANAGERS = ADMINS
# for sphinx
DATABASE_ENGINE   = 'postgresql_psycopg2'
DATABASE_NAME     = 'prospere'
DATABASE_USER     = 'postgres'
if DEBUG: DATABASE_PASSWORD = 'postgres'
else: DATABASE_PASSWORD = 'RSQ0WItYt1'
DATABASE_HOST     = '127.0.0.1'
DATABASE_PORT     = '5432'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': DATABASE_NAME,                      # Or path to database file if using sqlite3.
        'USER': DATABASE_USER,                      # Not used with sqlite3.
        'PASSWORD': DATABASE_PASSWORD,                  # Not used with sqlite3.
        'HOST': DATABASE_HOST,                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': DATABASE_PORT,                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name.
TIME_ZONE = 'Europe/Kiev'

# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'ru-RU'
#LANGUAGE_CODE = 'en-us'

SITE_ID = 1

APPEND_SLASH = False
# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = '/www/media/files/'
#MEDIA_ROOT = 'd:\\www\\media\\files'
TEST_MEDIA_ROOT = '/www/media/files/test/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/files/'

FILE_UPLOAD_PERMISSIONS = 0750
FILE_UPLOAD_TEMP_DIR = '/www/tmp/'
# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = '/www/prospere/static/'
#STATIC_ROOT = 'c:\\www\\prospere\\static\\'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

CSRF_FAILURE_VIEW = 'prospere.copia.views.csrf_failure'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'snp_o6d9qfg($$wvm@$jn3xy$ytrzxuw^0pty7nt@e#(+dp7=u'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
	'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'prospere.urls'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)
TEMPLATE_CONTEXT_PROCESSORS =(
	'django.contrib.auth.context_processors.auth',
	'django.core.context_processors.static',
	'prospere.copia.context_processors.url',
	#'prospere.copia.context_processors.my_page',
	'django.core.context_processors.request',
)
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.sites',
    #'django.contrib.messages',
    'prospere.copia',
    'prospere.contrib.account',
    'prospere.contrib.comment',
    'prospere.contrib.market',
    'prospere.contrib.cabinet',
    'prospere.contrib.notification',
    'mptt',
    'tinymce',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html':False,
        },
        'logfile': {
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': '/www/prospere.log',
        },
        'market_logfile': {
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': '/www/market.log',
        },
    },
    'loggers': {
        # Again, default Django configuration to email unhandled exceptions
        'django.request': {
            'handlers': ['logfile'],
            'level': 'ERROR',
            'propagate': True,
        },
        # Might as well log any errors anywhere else in Django
        'django': {
            'handlers': ['logfile'],
            'level': 'ERROR',
            'propagate': False,
        },
        # Your own app - this assumes all your logger names start with "myapp."
        'log': {
            'handlers': ['logfile'],
            'level': 'WARNING', # Or maybe INFO or DEBUG
            'propogate': False
        },
        'market_log': {
            'handlers': ['market_logfile'],
            'level': 'WARNING', # Or maybe INFO or DEBUG
            'propogate': False
        },
    },
}
# copia 
NUMBER_COMMENT_PER_PAGE = 8
EVERYONE_CAN_COMMENT = True
NUMBER_SEARCH_RESULT_PER_PAGE = 10
# Registration

REGISTRATION_OPEN = True

INSTALLED_APPS += ('registration',)
ACCOUNT_ACTIVATION_DAYS = 2 # кол-во дней для хранения кода активации
AUTH_PROFILE_MODULE = 'account.UserProfiles'
# для отправки кода активации
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'management@copia.org.ua'
EMAIL_HOST_PASSWORD = 'Y5tEmSHdA8'
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = 'management@copia.org.ua'

# SPHINX_SERVER = 'localhost'
# SPHINX_PORT = 3312
SPHINX_API_VERSION = 0x116
INSTALLED_APPS += ('djangosphinx',)
# tiny mce
TINYMCE_DEFAULT_CONFIG = {
    'plugins': "table,spellchecker,paste,searchreplace",
    #'plugins':"autolink,lists,pagebreak,style,layer,table,save,advhr,advimage,advlink,emotions,iespell,inlinepopups,insertdatetime,preview,media,searchreplace,print,contextmenu,paste,directionality,fullscreen,noneditable,visualchars,nonbreaking,xhtmlxtras,template,wordcount,advlist,autosave",
    'theme': "advanced",
    
    'theme_advanced_buttons1' : "bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,styleselect,formatselect,fontselect,fontsizeselect",
    'theme_advanced_buttons2' : "search,replace,|,bullist,numlist,|,outdent,indent,|,undo,redo,|,link,unlink,anchor,code,|,forecolor,backcolor|,sub,sup,|,charmap",
    'theme_advanced_buttons3' : "",

    'theme_advanced_toolbar_location' : "top",
	'theme_advanced_toolbar_align' : "left",
	'theme_advanced_statusbar_location' : "bottom",

}
TINYMCE_SPELLCHECKER = False
TINYMCE_COMPRESSOR = True
# Cabinet selttings
DOCUMENT_DESCRIPTION_MAX_LENGTH = 3000
ALLOW_GET_DOCUMENT_FILES = True
MAX_PATH_DEPTH = 5
#MARKET
ROBOKASSA_LOGIN = 'nickolas'
ROBOKASSA_PASSWORD1 = 'asdqwe'

# debug-панель
if DEBUG:
	MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
	INSTALLED_APPS += ('debug_toolbar',)
	INTERNAL_IPS = ('127.0.0.1',)

