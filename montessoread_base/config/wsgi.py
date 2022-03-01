import os

from django.core.wsgi import get_wsgi_application
from config.settings.base import EXEC_ENV

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.{}".format(EXEC_ENV.lower()))

application = get_wsgi_application()
