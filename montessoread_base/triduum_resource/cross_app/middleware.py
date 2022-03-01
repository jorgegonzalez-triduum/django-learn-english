import threading
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.utils.deprecation import MiddlewareMixin


_thread_locals = threading.local()

def get_current_request():
    '''Retorna el contenido del objeto Request actual.'''
    return getattr(_thread_locals, 'request', None)

def get_current_user():
    '''Retorna el usuario que se encuentra logueado en el sitio.'''
    request = get_current_request()

    if request:
        return request.user

    return None

def set_current_request(user):
    '''Asigna el superusuario al objeto Request actual.'''

    request = HttpRequest()
    request.user = user
    return setattr(_thread_locals, 'request', request)


class GlobalRequestMiddleware(MiddlewareMixin):

    def process_request(self, request):
        _thread_locals.request = request
