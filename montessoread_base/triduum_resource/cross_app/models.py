from django.db import models
from . import fields as self_fields
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User, Permission, Group
from django.core.cache import cache
from django.core.exceptions import ValidationError
from datetime import datetime
from .globals import permission_type
from .middleware import get_current_user, get_current_request
from django.utils.translation import gettext as _
# Create your models here.

class BaseManager(models.Manager):
    
    select_related_def = []
    prefetch_related_def = []
    
    def __init__(self, 
                select_related=[],
                prefetch_related=[],
                *args,
                **kwargs):
        self.select_related_def = []
        self.prefetch_related_def = []
        super().__init__(*args, **kwargs)
        
    def get_queryset(self):
        #return super().get_queryset().all()
        return super().get_queryset(
            ).select_related(*self.select_related_def
                ).prefetch_related(*self.prefetch_related_def
                    ).filter(disabled = False)

class Base(models.Model):
    '''
    This class defines attributes that allow auditing of information stored \
    In classes that inherit from it, it allows logical deletion of the \
    information in the database so that the code remains clean and \
    No redundancy of attributes.

        - ** disabled: ** Allows logical deletion of information in the \
            database, since when it is "deleted" the value of this is changed to \
            True Only information whose value in this field is False is consulted.
        - ** meta: ** This field will have the following structure: "default_meta"
    '''

    def default_meta():
        return {
            'created_at': '01/01/2017 00:00:00',
            'created_by': '',
            'modified_at': '01/01/2017 00:00:00',
            'modified_by': '',
        }

    meta = JSONField(editable = False, default = default_meta)
    disabled = models.NullBooleanField(_('Deactivate'), default = False)
    objects = BaseManager()
    alls = models.Manager()

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        if not getattr(self, 'clear_cache', False):
            self.clear_cache = False
        super().__init__(*args, **kwargs)
        self.__metainit__()

    def __metainit__(self):
        self.created_at = self.get_meta_date('created_at')
        self.modified_at = self.get_meta_date('modified_at')

    def get_meta_user(self, user_field_name):
        if user_field_name in self.meta and self.meta[user_field_name]:
            try:
                return User.objects.get(username = self.meta[user_field_name])
            except:
                return self.meta[user_field_name]

        return None

    def get_meta_date(self, date_field_name):
        if date_field_name in self.meta and self.meta[date_field_name]:
            return datetime.strptime(self.meta[date_field_name], '%d/%m/%Y %H:%M:%S')

        return None

    def versioning(self):
        return False

    def bulk_create(self, objs, batch_size=None, *args, **kwargs):
        if 'username' in kwargs:
            username = kwargs.pop('username')
        else:
            username = get_current_user().username
        self.meta['created_at'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.meta['created_by'] = username
        self.meta['modified_at'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.meta['modified_by'] = username

        return self.__class__.objects.bulk_create(objs)

    def save(self, force_insert = False, force_update = False, *args, **kwargs):
        ''' Doc: pending '''
        if 'username' in kwargs:
            username = kwargs.pop('username')
        else:
            username = get_current_user().username

        if not self.id or force_insert:
            self.meta['created_at'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            self.meta['created_by'] = username
            self.meta['modified_at'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            self.meta['modified_by'] = username
        else:
            self.meta['modified_at'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            self.meta['modified_by'] = username
        if self.clear_cache:
            cache.clear()
        return super(Base, self).save(*args, **kwargs)

    def disable(self):
        '''Realiza el borrado lógico (cambio de estado) en base de datos.'''
        # No se hizo con disabled True para manejar 3 estados. True/False/None. JMG
        self.disabled = None
        self.save(force_update=True)


class CompanyInformation(Base):


    company_name = models.CharField(_('Company name'), max_length=200)
    light_logo = self_fields.AutoWebpFileField(upload_to='company_information/logos/',
            verbose_name='_(Light logo)', null=True, blank=True
            )
    dark_logo = self_fields.AutoWebpFileField(upload_to='company_information/logos/',
            verbose_name='_(Dark logo)', null=True, blank=True
            )
    short_light_logo = self_fields.AutoWebpFileField(upload_to='company_information/logos/',
            verbose_name='_(Short light logo)', null=True, blank=True
            )
    short_dark_logo = self_fields.AutoWebpFileField(upload_to='company_information/logos/',
            verbose_name='_(Short light logo)', null=True, blank=True
            )
    primary_color =  models.CharField(_('Primary color'), max_length=20, null=True, blank=True)
    phone_number = models.CharField(_('Phone number'), max_length=200, null=True, blank=True)
    whatsapp_number = models.CharField(_('Whatsapp number'), max_length=200, null=True, blank=True)
    contact_email = models.EmailField(_('Contact email'))
    support_email = models.EmailField(_('Support email'), null=True, blank=True)
    instagram_name = models.CharField(_('Instagram profile name'), max_length=200, null=True, blank=True)
    instagram_url = models.CharField(_('Instagram url'), max_length=200, null=True, blank=True)
    facebook_name = models.CharField(_('Facebook profile name'), max_length=200, null=True, blank=True)
    facebook_url = models.CharField(_('Facebook url'), max_length=200, null=True, blank=True)
    extra_fields = JSONField(verbose_name='_(Extra fields)',default=dict)

    class Meta:
        verbose_name = _("Company information")
        verbose_name_plural = _("Company informations")

    def save(self, *args, **kwargs):
        if not self.id and self.__class__.objects.all().exists():
            raise AssertionError(
                _('There can be no more than one corporate information record.')
                )
        else:
            return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError(_('A company information cannot be deleted')) 
    
    def __str__(self):
        return _('Company information')


def get_user_photo_folder(instance, filename):
    return 'user/{0}/photo/{1}'.format(instance.user.id, filename)

class UserInfo(Base):
    
    objects = BaseManager(select_related=['user'])
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_info")
    photo = self_fields.AutoWebpImageField(upload_to=get_user_photo_folder,
            verbose_name='_(Photo)', null=True, blank=True
            )
    
    def __str__(self):
        return str(self.user.username)


class AppPermission(Base):

    PERMISSION_TYPE = (
        (permission_type.section, _('Section')),
        (permission_type.funcionality, _('Funcionality'))
    )
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    permission_type = models.PositiveSmallIntegerField(choices=PERMISSION_TYPE)

    def delete(self, *args, **kwargs):
        if self.permission:
            perm = self.permission 
            perm.codename = '{}-deleted'.format(
                perm.codename
            )
            perm.save()
        return super().delete(*args,**kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['disabled', 'permission', 'permission_type'],
                name="disabled-permission-permission_type")
        ]

class GroupInfo(Base):
    
    objects = BaseManager(select_related=['group'])
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name="group_info")
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.group.name)
    
class AppSection(Base):
    
    '''
        Front end routed section
    '''
    clear_cache = True
    
    app_permission = models.ForeignKey(AppPermission, on_delete=models.CASCADE, null=True, blank=True)
    parent = models.ForeignKey(_('AppSection'), on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(_('Name'), max_length=150)
    path = models.CharField(_('Path to route'), max_length=150, null=True, blank=True, unique=True)
    hover_text = models.CharField(_('Hover text'), max_length=1300, null=True, blank=True)
    icon_name = models.CharField(_('Icon name'), max_length=20, null=True, blank=True)
    admin_required = models.BooleanField(_('Admin required?'), default = False)
    order = models.PositiveSmallIntegerField(_('Order'), default=1)
    users = models.ManyToManyField(User, related_name="app_sections_users")
    
    def __str__(self):
        return '{} - {}'.format(
            str(self.id),        
            str(self.name))

    def get_parent_tree(self):
        iter_obj = self
        parent_tree = [iter_obj]#Recursive obj iterated
        if iter_obj.parent:
            while iter_obj.parent:
                iter_obj = iter_obj.parent
                parent_tree.append(iter_obj)
        return parent_tree[::-1]

    def save(self, *args, **kwargs):
        if len(self.get_parent_tree()) > 3:
            raise ValidationError(
                _("You cannot create more than 3 levels in a menu")
                )
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.app_permission.delete()
        return super().delete(*args, **kwargs)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['disabled', 'path'],
                name="unique_togheter")
        ]
        ordering = ['order']