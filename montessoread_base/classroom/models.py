from django.db import models
from django.utils.translation import gettext as _
from triduum_resource.cross_app.models import Base
from classroom import globals as choices


class Student(Base):

    GENDER_STATUS = (
        (choices.gender_type.male[0], choices.gender_type.male[1]),
        (choices.gender_type.female[0], choices.gender_type.female[1]),
    )
    
    name = models.CharField(_('Name'),  max_length=50)       
    surname = models.CharField(_('Surname'),  max_length=50)      
    gender = models.PositiveSmallIntegerField(_('Gender'), choices=GENDER_STATUS)
    birth_date = models.DateField(_('Birth date'))