"""
Django installed apps
"""

from .env import DEBUG


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
    'post_office',
    'django_extensions',

    'crispy_forms',  # Form layouts
    'bootstrapform',
    'allauth_bootstrap',
    'allauth',  # Authentication
    'allauth.account',
    'phonenumber_field',  # Support for phone numbers
    'formtools',  # multipage wizard forms
    'betterforms',
    'dal',  # django-autocomplete-light
    'dal_select2',
    'import_export',
    'django_tables2',

    'solo',

    # And add admin after django-autocomplete-light:
    'django.contrib.admin',

    # Local apps:
    'users',
    'annuaire'
]

if DEBUG:
    INSTALLED_APPS += ['whitenoise.runserver_nostatic']
