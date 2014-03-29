DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('test@example.com', 'Administrator'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'connections',
    'tests',
)

CACHE_BACKEND = 'locmem://'

SECRET_KEY = 'thats-a-secret'
