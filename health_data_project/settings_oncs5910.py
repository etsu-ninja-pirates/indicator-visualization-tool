# Do NOT use `import settings` in here - that will cause an infinite import loop!
# Similarly, this file will NOT work unless imported inside settings.py
# (We use variables defined in that file!)
import os

# bummer we have to do this twice, but not sure how else to get it
# without recursively referring to the base settings.py file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_secret(file):
	path = os.path.join(BASE_DIR, file)
	with open(path) as f:
		return f.read().strip()

SECRET_KEY = load_secret('secret_key.txt')

ALLOWED_HOSTS = ['localhost', '151.141.91.27']

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql',
		'NAME': 'hds_app_db',
		'USER': 'hds_app',
		'PASSWORD': load_secret('database_password.txt'),
		'HOST': 'localhost',
		'PORT': '5432',
	}
}

STATIC_ROOT = '/home/hds-app/static/'

MEDIA_ROOT = '/home/hds-app/media/'