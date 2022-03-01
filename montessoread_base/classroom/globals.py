from collections import namedtuple
from django.utils.translation import gettext as _

GenderType = namedtuple(
    'GenderType', ['male', 'female'])
gender_type = GenderType((1, _('Male')), (2, _('Female')))