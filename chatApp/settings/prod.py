from .base import *


DEBUG=False

ADMINS = [
    ('matata', '254khoi@gmail.com'),
]

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']

REDIS_URL = 'redis://cache:6379'
CHANNEL_LAYERS['default']['CONFIG']['hosts'] = [REDIS_URL]

DATABASES = {
    'default':{
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': 'bernie101',
        'HOST': 'db',
        'PORT': 5432,
    }
}



