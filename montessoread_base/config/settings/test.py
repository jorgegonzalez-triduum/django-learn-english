from triduum_resource.cross_app.settings.base import *

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATIC_ROOT = '/var/www/static/montessoread_base/'
MEDIA_ROOT = '/var/www/media/montessoread_base/'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Enable for custom error pages
DEBUG_TRACEBACK = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE':       get_secret("ENGINE_DB_TEST"),
        'NAME':         get_secret("NAME_DB_TEST"),
        'USER':         get_secret("USER_DB_TEST"),
        'PASSWORD':     get_secret("PASSWORD_DB_TEST"),
        'HOST':         get_secret("HOST_DB_TEST"),
        'PORT':         get_secret("PORT_DB_TEST"),
    }
}

# Included in from triduum_resource.cross_app.settings.base import *
JWT_AUTH['JWT_RESPONSE_PAYLOAD_HANDLER'] = 'config.drf_payloads.jwt_response_payload_handler'