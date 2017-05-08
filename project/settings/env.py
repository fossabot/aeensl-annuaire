import environ
import sys

ROOT_DIR = environ.Path(__file__) - 3
APPS_DIR = ROOT_DIR.path('apps')
sys.path.insert(0, str(APPS_DIR))

env = environ.Env()
env.read_env(ROOT_DIR(".env"))

SECRET_KEY = env('DJANGO_SECRET_KEY')
DEBUG = env.bool('DJANGO_DEBUG', False)
