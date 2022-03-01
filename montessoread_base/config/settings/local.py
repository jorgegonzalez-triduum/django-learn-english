from triduum_resource.cross_app.settings.base import *

STATIC_URL = '/static/'

MEDIA_URL = '/media/'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Enable for custom error pages
DEBUG_TRACEBACK = True

ALLOWED_HOSTS = ['*']

MEDIA_ROOT = '{}{}'.format(BASE_DIR, '/media')

DATABASES = {
    'default': {
        'ENGINE':       get_secret("ENGINE_DB_LOCAL"),
        'NAME':         get_secret("NAME_DB_LOCAL"),
        'USER':         get_secret("USER_DB_LOCAL"),
        'PASSWORD':     get_secret("PASSWORD_DB_LOCAL"),
        'HOST':         get_secret("HOST_DB_LOCAL"),
        'PORT':         get_secret("PORT_DB_LOCAL"),
    }
}

# Included in from triduum_resource.cross_app.settings.base import *
JWT_AUTH['JWT_RESPONSE_PAYLOAD_HANDLER'] = 'config.drf_payloads.jwt_response_payload_handler'