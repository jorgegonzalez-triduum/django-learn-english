from ..rest_framework.settings import *
from ..rest_framework_jwt.settings import *
from config.settings.base import *

MIDDLEWARE += ['triduum_resource.cross_app.middleware.GlobalRequestMiddleware']