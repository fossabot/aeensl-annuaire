from .env import ROOT_DIR

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

# Sending emails with django-post_office
# --------------------------------------

EMAIL_BACKEND = 'post_office.EmailBackend'
ACCOUNT_EMAIL_SUBJECT_PREFIX = "[AE ENS]"
EMAIL_SUBJECT_PREFIX = "[AE ENS] "
DEFAULT_FROM_EMAIL = "webmestre@lyon-normalesup.org"


# STORAGE CONFIGURATION
# ---------------------

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MEDIA_ROOT = ROOT_DIR('media_storage')
MEDIA_TMP = ROOT_DIR('media_storage/tmp')
MEDIA_URL = '/media/'
