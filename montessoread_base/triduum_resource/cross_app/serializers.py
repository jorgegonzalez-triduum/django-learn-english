from django.utils import timezone
from django.contrib.auth.models import User, Group, Permission
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db.models import Q
from triduum_resource.cross_app.utils.user_app_section import get_user_app_sections_tree
from triduum_resource.cross_app.models import (
    AppPermission, AppSection, UserInfo , GroupInfo, CompanyInformation)
from triduum_resource.cross_app.globals import permission_type
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from django.utils.translation import gettext as _
from django.conf import settings


class InitHyperlinkedModelSerializer(serializers.HyperlinkedModelSerializer):
    
    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)
        remove_fields = kwargs.pop('remove_fields', None)
        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)
        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
        elif remove_fields is not None:
            existing = set(self.fields)
            for field_name in existing:
                if field_name in remove_fields:
                    self.fields.pop(field_name)

class ContentTypeSerializer(InitHyperlinkedModelSerializer):
    """
    retrieve:
    Return the given content type.
    list:
    Return a list of all the existing content types.
    create:
    Create a new match instance.
    """
    class Meta:
        model = ContentType
        fields = ['url', 'id', 'app_label', 'model']

class UserGroupSerializer(InitHyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ['url', 'username', 'first_name', 'last_name']   

class GroupPermissionSerializer(InitHyperlinkedModelSerializer):

    class Meta:
        model = Group
        fields = ['url', 'name']
class PermissionSerializer(InitHyperlinkedModelSerializer):
    
    #content_type = ContentTypeSerializer(read_only=True)
    user_set_info = UserGroupSerializer(source="user_set", many=True, read_only=True)
    group_set_info = GroupPermissionSerializer(source="group_set", many=True, read_only=True)

    class Meta:
        model = Permission
        fields = ['url', 'id', 'name', 'codename',
            'content_type', 'user_set', 'group_set',
            'user_set_info', 'group_set_info']
        extra_kwargs = {
            'content_type': {'read_only': True},
            'user_set': {'read_only': True},
            'group_set': {'read_only': True}}
        
    def create(self, validated_data):
        content_type = ContentType.objects.get(app_label="auth", model="permission")
        validated_data['content_type'] = content_type
        try:
            Permission.objects.get(
                codename=validated_data['codename'],
                content_type=validated_data['content_type']
                )
        except ObjectDoesNotExist:
            instance = Permission.objects.create(**validated_data)
        else:
            raise serializers.ValidationError(
                {
                    'detail': _('A permission with the indicated name already exists')
                })
        return instance

class GroupInfoSerializer(InitHyperlinkedModelSerializer):
    
    class Meta:
        model = GroupInfo
        fields = ['url', 'group', 'description']

class GroupSerializer(InitHyperlinkedModelSerializer):
    
    permissions_info = PermissionSerializer(source='permissions',
        read_only=True, many=True, remove_fields=['user_set_info', 'group_set_info'])
    users_set_info = UserGroupSerializer(source='user_set',read_only=True, many=True)
    group_info = GroupInfoSerializer(read_only=True, many=False)
    
    class Meta:
        model = Group
        fields = [
            'url', 'id', 'name', 'permissions', 
            'permissions_info', 'user_set', 'group_info',
            'users_set_info']

    def create(self, validated_data):
        instance = super().create(validated_data)
        self.update_group_info_fields(instance, validated_data)
        return Group.objects.get(pk = instance.pk)

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        self.update_group_info_fields(instance, validated_data)
        return Group.objects.get(pk = instance.pk)
    
    def update_group_info_fields(self, instance, validated_data):
        request = self.context['request']
        data = {'group': GroupSerializer(
                        instance=instance,
                        context={'request':request}
                        ).data['url'],
                'description': request.data.get('description')
                }
        try:
            group_info_instance = GroupInfo.objects.get(group=instance)
        except ObjectDoesNotExist:
            group_info_instance = None
        if group_info_instance:
            u_i_srlzr = GroupInfoSerializer(instance=group_info_instance, data=data)
        else:
            u_i_srlzr = GroupInfoSerializer(data=data)
        if u_i_srlzr.is_valid():
            u_i_srlzr.save()
        else:
            raise serializers.ValidationError({'detail': u_i_srlzr.errors})    
        return group_info_instance


    # def update(self, instance, validated_data):
    #     instance.name = validated_data.get('name', instance.name)
    #     permissions = validated_data.get('permissions')
    #     if isinstance(permissions, list):
    #         instance.permissions.clear()
    #         for perm in validated_data.get('permissions', []):
    #             try:
    #                 instance.permissions.add(
    #                     Permission.objects.get(**perm)
    #                 )
    #             except ObjectDoesNotExist:
    #                 raise serializers.ValidationError(
    #                 {
    #                     'detail': _('Permissions not found, please try later')
    #                 })
    #     instance.save()
    #     return instance

class AppPermissionSerializer(InitHyperlinkedModelSerializer):
    '''
        This model was created to extend the permission
        base of Django and only manipulate relations
        with AppPermission
    '''
    permission = PermissionSerializer(remove_fields=['user_set_info', 'group_set_info'])
    permission_type_verbose = serializers.SerializerMethodField()
    
    class Meta:
        model = AppPermission
        fields = ['url', 'id', 'meta', 'permission', 
                'description', 'permission_type', 'permission_type_verbose']
    
    def get_permission_type_verbose(self, instance):
        return instance.get_permission_type_display()
            
    def create(self, validated_data):
        permission_serializer = PermissionSerializer(
            remove_fields=['user_set_info', 'group_set_info'], 
            data=validated_data['permission'])
        if permission_serializer.is_valid():
            try:
                permission_instance = Permission.objects.get(**validated_data['permission'])
            except ObjectDoesNotExist:
                permission_serializer.save()
                permission_instance = permission_serializer.instance
        else:
            raise serializers.ValidationError(permission_serializer.errors)
        if not AppPermission.objects.filter(
                permission=permission_instance,
                permission_type=validated_data['permission_type']
            ).exists():
            return AppPermission.objects.create(
                permission=permission_instance, 
                description=validated_data.get('description'),
                permission_type=validated_data['permission_type']
            )
        else:
            raise serializers.ValidationError({
                'detail': _('AppPermission already exists')
            })

    def update(self, instance, validated_data):
        permission_srlzr = PermissionSerializer(
            remove_fields=['user_set_info', 'group_set_info'],
            instance=instance.permission,
            data = validated_data['permission'])
        if permission_srlzr.is_valid():
            permission_srlzr.save()
        else:
            raise serializers.ValidationError(
                permission_srlzr.errors)
        new_instance = AppPermission.objects.get(pk = instance.pk)
        new_instance.description = validated_data.get('description')
        new_instance.save()
        return new_instance

class AppPermissionDetailSerializer(AppPermissionSerializer):
    permission = PermissionSerializer()

class AppSectionSerializerForUserTree(InitHyperlinkedModelSerializer):
    
    class Meta:
        model = AppSection
        fields = ['url', 'id', 'name', 'path', 
                'hover_text', 'icon_name', 'admin_required', 'app_permission']
    

class AppSectionSerializerBase(InitHyperlinkedModelSerializer):

    app_permission = AppPermissionSerializer(read_only=True)
    parent_tree = serializers.SerializerMethodField()
    
    class Meta:
        model = AppSection
        fields = ['url', 'id', 'name', 'path',
                'hover_text', 'icon_name',
                'parent', 'admin_required', 'app_permission',
                'parent_tree']
        
    def get_parent_tree(self,instance):
        return {}

class AppSectionSerializer(AppSectionSerializerBase):
    
    parent_tree = AppSectionSerializerBase(source="get_parent_tree",read_only=True, many=True)
    
    def update_app_permission(self, data, validated_data, instance):
        app_permission = data.get('app_permission', "")
        if isinstance(app_permission, bool):
            if app_permission:
                if instance and instance.app_permission:
                    return instance.app_permission
                a_p_name = 'Section {} permission'.format(validated_data[
                    'name'].lower().replace(' ','_'))
                a_p_code_name = 'section_perm_{}'.format(validated_data[
                    'name'].lower().replace(' ','_'))
                app_permission_srlzr = AppPermissionSerializer(data= {
                        "permission": {
                            "name": a_p_name,
                            "codename": a_p_code_name
                        },
                        "description": a_p_name,
                        "permission_type": permission_type.section 
                })
                if app_permission_srlzr.is_valid():
                    app_permission_srlzr.save()
                    instance.app_permission = app_permission_srlzr.instance
                else:
                    raise serializers.ValidationError(
                        app_permission_srlzr.errors
                    )
            else:
                app_permission = None
                if instance.app_permission:
                    app_permission = instance.app_permission
                    perm = app_permission.permission
                    perm.delete()
                    app_permission.delete()
                instance.app_permission = None
        instance.save()
        return instance
    
    def create(self, validated_data):
        try:
            instance = super().create(validated_data)
        except Exception as e:
            raise serializers.ValidationError({'detail': e})
        data = self.context['request'].data
        instance = self.update_app_permission(
            data, validated_data, instance)
        return instance

    def update(self, instance, validated_data):
        try:
            instance = super().update(instance,validated_data)
        except Exception as e:
            raise serializers.ValidationError({'detail': e})
        data = self.context['request'].data
        self.update_app_permission(
            data, validated_data, instance)
        return instance

class UserInfoSerializer(InitHyperlinkedModelSerializer):
    
    class Meta:
        model = UserInfo
        fields = ['user', 'photo', 'url']
        extra_kwargs = {'password': {'read_only': True}}

class UpdateUserPhotoSerializer(InitHyperlinkedModelSerializer):

    class Meta:
        model = UserInfo
        fields = ['user', 'photo', 'url']

class PasswordSerializer(InitHyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ['url', 'id', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance

class UserSerializer(InitHyperlinkedModelSerializer):
    
    groups_detail = GroupSerializer(source='groups', many=True, read_only=True)
    app_sections_tree = serializers.SerializerMethodField()
    #user_info = serializers.SerializerMethodField()
    user_info = UserInfoSerializer(read_only=True, many=False) # many=True is required
    app_user_permissions_detail = serializers.SerializerMethodField()
    user_permissions_filtered = serializers.SerializerMethodField()
    subscription_active = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'url', 'id', 'username', 'first_name', 
            'last_name', 'email', #'is_staff',
            'is_superuser','is_active', 
            'user_info', 'groups','groups_detail', 
            'user_permissions', 'user_permissions_filtered',
            'app_user_permissions_detail', 
            'app_sections_users',
            'app_sections_tree', 'subscription_active']

    def get_user_permissions_filtered(self, instance):
        ''' Excluding sections permissions '''
        all_perms = instance.user_permissions.all()
        filtered_perms = AppPermission.objects.filter(
            permission__in = all_perms,
            permission_type = permission_type.funcionality)
        return [x['url'] for  x in PermissionSerializer(
            fields=['url'],
            instance=[x.permission for x in filtered_perms],
            many=True, context={
                'request': self.context[
                    'request']}).data]

    def get_subscription_active(self, instance):
        subscription = instance.usersubscription_set.all().last()
        active = False
        if subscription and subscription.disabled == False:
            if subscription.end_date:
                if subscription.start_date <= timezone.now() and timezone.now() <= subscription.end_date:
                    active = True
            else:
                if timezone.now() >= subscription.start_date:
                    active = True
        return active
    
    def get_app_user_permissions_detail(self, instance):
        user_all_perms = Permission.objects.filter(
            Q(group__in=instance.groups.all())|Q(user=instance)
            ).distinct()
        app_perms_user = AppPermission.objects.filter(
            permission__in=user_all_perms)
        return AppPermissionSerializer(
            app_perms_user, many=True, context={
                'request': self.context['request']}).data
        
    def get_app_sections_tree(self, instance):
        request = self.context['request']
        serialized_section_trees = []
        section_trees_instances = get_user_app_sections_tree(instance)
        cache_key = '{}_sections_tree'.format(
            instance.username
        )
        if settings.EXEC_ENV != 'LOCAL':
            cached_tree = cache.get(cache_key)
        else:
            cached_tree = None
        if not cached_tree:
            for sti in section_trees_instances:
                srlzd_sti = AppSectionSerializerForUserTree(
                    instance=sti,
                    context={'request': request}).data
                if sti.children.exists():
                    srlzd_sti['children'] = []
                    for fchild_sti in sti.children: # First child
                        srlzd_f_ch = AppSectionSerializerForUserTree(
                            instance=fchild_sti,
                            context={'request': request}).data
                        if fchild_sti.children.exists():
                            srlzd_f_ch['children'] = []
                            for schild_sti in fchild_sti.children: # Second child
                                srlzd_f_ch['children'].append(
                                    AppSectionSerializerForUserTree(
                                    instance=schild_sti,
                                    context={'request': request}).data
                                )
                        srlzd_sti['children'].append(
                            srlzd_f_ch
                        )
                serialized_section_trees.append(
                    srlzd_sti
                    )
            cache.set(cache_key, serialized_section_trees, 3600)
        else:
            serialized_section_trees = cached_tree
        return serialized_section_trees
    
    def update_user_info_fields(self, instance, validated_data):
        request = self.context['request']
        data = {'user': UserSerializer(
                        instance=instance,
                        context={'request':request}
                        ).data['url'],
                'photo': request.data.get('photo')
                }
        try:
            user_info_instance = UserInfo.objects.get(user=instance)
        except ObjectDoesNotExist:
            user_info_instance = None
        if user_info_instance:
            u_i_srlzr = UserInfoSerializer(instance=user_info_instance, data=data)
        else:
            u_i_srlzr = UserInfoSerializer(data=data)
        if u_i_srlzr.is_valid():
            u_i_srlzr.save()
        else:
            raise serializers.ValidationError({'detail': u_i_srlzr.errors})    
        return user_info_instance
        
    def update_user_password(self,instance, validated_data):
        data = self.context['request'].data
        password = data.get('password')
        if not isinstance(password, type(None)):
            if password:
                pw_srlzr = PasswordSerializer(
                    instance=instance,
                    data=data)
                if pw_srlzr.is_valid():
                    pw_srlzr.save()
        
    def update_user_perms_by_sections(self, instance):
        for section in instance.app_sections_users.all():
            if section.app_permission:
                instance.user_permissions.add(section.app_permission.permission)
        return instance
        
    def create(self, validated_data):
        instance = super().create(validated_data)
        self.update_user_password(instance, validated_data)
        self.update_user_info_fields(instance, validated_data)
        return User.objects.get(pk = instance.pk)

    def update(self, instance, validated_data):
        instance.user_permissions.clear()
        instance = super().update(instance, validated_data)
        return self.update_user_perms_by_sections(instance)

class CompanyInformationFilesSerializer(InitHyperlinkedModelSerializer):
    
    class Meta:
        model = CompanyInformation
        fields = ('light_logo', 'dark_logo', 'short_light_logo', 'short_dark_logo')

class CompanyInformationSerializer(InitHyperlinkedModelSerializer):
    
    class Meta:
        model = CompanyInformation
        fields = '__all__'
        extra_kwargs = {
            'light_logo': {'read_only': True},
            'dark_logo': {'read_only': True},
            'short_light_logo': {'read_only': True},
            'short_dark_logo': {'read_only': True},
        }
    
    def create(self, validated_data):
        try:
            instance = super().create(validated_data)
        except AssertionError as e:
            raise serializers.ValidationError({
                'detail': e
            })
        return instance

    def update_user_info_fields(self, instance, validated_data):
        request = self.context['request']
        data = {'user': UserSerializer(
                        instance=instance,
                        context={'request':request}
                        ).data['url'],
                'photo': request.data.get('photo')
                }
        try:
            user_info_instance = UserInfo.objects.get(user=instance)
        except ObjectDoesNotExist:
            user_info_instance = None
        if user_info_instance:
            u_i_srlzr = UserInfoSerializer(instance=user_info_instance, data=data)
        else:
            u_i_srlzr = UserInfoSerializer(data=data)
        if u_i_srlzr.is_valid():
            u_i_srlzr.save()
        else:
            raise serializers.ValidationError({'detail': u_i_srlzr.errors})    
        return user_info_instance