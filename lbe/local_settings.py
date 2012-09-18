__author__ = 'Bruno Bonfils bbonfils@opencsi.com'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'lbe',                        # Or path to database file if using sqlite3.
        'USER': 'lbe',                        # Not used with sqlite3.
        'PASSWORD': 'lbepassword',            # Not used with sqlite3.
        'HOST': '',                           # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                           # Set to empty string for default. Not used with sqlite3.
    }
}

LDAP_SERVER = {
'HOST': 'localhost',
'PORT': 1389,
'BASE_DN': 'dc=opencsi,dc=com',
'BIND_DN': 'cn=Directory Manager',
'BIND_PWD': 'toto'
}

MONGODB_SERVER = {
'HOST': 'localhost',
'PORT': 27017,
'DATABASE': 'lbe',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'db': {
            #'level': 'DEBUG',
            'class': 'services.loggerHandler.logDB',#'logging.StreamHandler',
        },
        'request': {
            #'level': 'DEBUG',
            'class': 'services.loggerHandler.logRequest',#'logging.StreamHandler',
        }
    },
    'loggers': {
        'services': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
            },
        'dao': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
            },
        '': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
            },
        }
}