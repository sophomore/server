from pos_server.settings.base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'pos',
        'USER': 'song',
        'PASSWORD': 'Qoswlfdlsnrn',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': 'SET character_set_connection=utf8,'
                            'collation_connection=utf8_general_ci,foreign_key_checks = 0,'
                            'sql_mode = "";',
            'charset': 'utf8',
            'use_unicode': True,
        },
    }
}

DEBUG = True
MEDIA_URL = 'http://localhost:8000' + MEDIA_URL

HOSTNAME = '0.0.0.0'