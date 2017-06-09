"""
Django installed apps
"""

from .env import DEBUG

DJANGO_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

CONTRIB_APPS = [
    'raven.contrib.django.raven_compat',  # Sentry
    'compressor',  # take care of static files
    'compressor_toolkit',  # addon for django-compressor
    'post_office',
    'django_extensions',

    # Logic states
    'django_fsm',
    'django_fsm_log',
    'fsm_admin',

    # Forms and templates
    'crispy_forms',  # Form layouts
    'bootstrapform',
    'phonenumber_field',  # Support for phone numbers
    'formtools',  # multipage wizard forms
    'betterforms',
    'dal',  # django-autocomplete-light
    'dal_select2',
    'django_tables2',

    'allauth_bootstrap',
    'allauth',  # Authentication
    'allauth.account',

    'import_export',
    'solo',
    'django.contrib.admin',
]

if DEBUG:
    CONTRIB_APPS += ['whitenoise.runserver_nostatic']

PROJECT_APPS = [
    'users',
    'annuaire'
]

INSTALLED_APPS = DJANGO_APPS + CONTRIB_APPS + PROJECT_APPS
