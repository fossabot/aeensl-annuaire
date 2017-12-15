from .env import env, ROOT_DIR


ALLOWED_HOSTS = [
    'localhost', '127.0.0.1', '[::1]',
    'annuaire-dev.herokuapp.com',
    'adherent.lyon-normalesup.org',
    'adherent-dev.lyon-normalesup.org'
]

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',

    # Log 404 errors using Sentry
    'raven.contrib.django.raven_compat.middleware.Sentry404CatchMiddleware',

    # Default Django middlewares:
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Third party middlewares
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',
)

ROOT_URLCONF = 'project.urls'
WSGI_APPLICATION = 'project.wsgi.application'
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
