import environ
import raven

ROOT_DIR = environ.Path(__file__) - 2
APPS_DIR = ROOT_DIR.path('annuaire')

env = environ.Env()
env.read_env(ROOT_DIR(".env"))

SECRET_KEY = env('DJANGO_SECRET_KEY')
DEBUG = env.bool('DJANGO_DEBUG', False)

ALLOWED_HOSTS = [
    'localhost', '127.0.0.1', '[::1]',
    'annuaire-dev.herokuapp.com',
    'adherent.lyon-normalesup.org']

# APPLICATION DEFINITION

INSTALLED_APPS = [
    # Default Django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Third party apps:
    'raven.contrib.django.raven_compat',  # Sentry
    'compressor',  # take care of static files
    'compressor_toolkit',  # addon for django-compressor

    # Local apps:
    'users',

    'crispy_forms',  # Form layouts
    'bootstrapform',
    'allauth_bootstrap',
    'allauth',  # Authentication
    'allauth.account',
    'phonenumber_field',  # Support for phone numbers
    'formtools',  # multipage wizard forms
    'dal',  # django-autocomplete-light
    'dal_select2',

    'solo',

    # And add admin after django-autocomplete-light:
    'django.contrib.admin',
]

if DEBUG:
    INSTALLED_APPS += ['whitenoise.runserver_nostatic']

MIDDLEWARE = (
    # Log 404 errors using Sentry
    'raven.contrib.django.raven_compat.middleware.Sentry404CatchMiddleware',

    # Default Django middlewares:
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Third party middlewares
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',
)

ROOT_URLCONF = 'annuaire.urls'
WSGI_APPLICATION = 'annuaire.wsgi.application'
SITE_ID = 1

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ROOT_DIR('templates'), ROOT_DIR('templates/users'), ROOT_DIR('templates/allauth')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'


# Database
# --------

DATABASES = {
    'default': env.db('DATABASE_URL', default='postgres:///annuaire'),
}
DATABASES['default']['ATOMIC_REQUESTS'] = True


# STORAGE CONFIGURATION
# ---------------------

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MEDIA_ROOT = ROOT_DIR('media_storage')
MEDIA_TMP = ROOT_DIR('media_storage/tmp')
MEDIA_URL = '/media/'


# AUTHENTICATION CONFIGURATION
# ----------------------------

ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True

ACCOUNT_ALLOW_REGISTRATION = False  # No manual registration
LOGIN_REDIRECT_URL = 'current_user_profile'

# Custom user app defaults
AUTH_USER_MODEL = 'users.User'

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'fr-FR'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_L10N = True
USE_TZ = True

PHONENUMBER_DB_FORMAT = 'NATIONAL'
PHONENUMBER_DEFAULT_REGION = 'FR'


# Static files (CSS, JavaScript, Images)
# --------------------------------------

STATIC_ROOT = ROOT_DIR('staticfiles')
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    ROOT_DIR('assets'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',

    # Third party finders:
    'npm.finders.NpmFinder',
)

COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'compressor_toolkit.precompilers.SCSSCompiler'),
)


# Monitoring with Sentry
# ----------------------

RAVEN_CONFIG = {
    'dsn': env('SENTRY_DSN', default=None),
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    'release': raven.fetch_git_sha(str(ROOT_DIR)),
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'ERROR', # To capture more than ERROR, change to WARNING, INFO, etc.
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'tags': {'custom-tag': 'x'},
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}

if DEBUG:
    RAVEN_CONFIG = {}
    LOGGING = {}
