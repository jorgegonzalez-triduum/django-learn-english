from triduum_resource.cross_app.serializers import InitHyperlinkedModelSerializer
from rest_framework import serializers
from classroom.models import Student
from platform_settings.serializers import UserSubscriptionSerializer
from platform_settings import models as PlatformSettingsModels


class StudentSerializer(InitHyperlinkedModelSerializer):
    
    '''
    Part of this serializer was replicated in courses_management serializers due to
    circular import issue.
    '''
    
    full_name = serializers.SerializerMethodField()
    gender_display = serializers.CharField(source="get_gender_display", required=False)
    gender = serializers.IntegerField()
    usersubscription_set = serializers.SerializerMethodField()
    usersubscription_info = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'url', 'full_name', 'name', 'surname', 'gender',
            'gender_display', 'studentsubscription_set',
            'usersubscription_set', 'usersubscription_info', 'birth_date', 'playexercise_set']
        extra_kwargs = {
            'playexercise_set' : { 'read_only': True },
            'studentsubscription_set' : { 'read_only': True },
            'usersubscription_set' : { 'read_only': True },
        }

    def get_full_name(self, instance):
        return f"{instance.name} {instance.surname}".strip()
    
    def get_usersubscription_set(self, instance):
        return [
            UserSubscriptionSerializer(
                fields=['id'],
                instance=x.user_subscription,
                context={'request': self.context['request']}
                ).data['id']
            for x in instance.studentsubscription_set.all()
        ]

    def get_usersubscription_info(self, instance):
        return [
            UserSubscriptionSerializer(
                fields=['url', 'id', 'user_info', 'name'],
                instance=x.user_subscription,
                context={'request': self.context['request']}
                ).data
            for x in instance.studentsubscription_set.all()
        ]
    
    def update_student_user_subscriptions(self, student_instance, validated_data):
        if 'usersubscription_set' in self.context['request'].data:
            usersubscription_set = self.context['request'].data['usersubscription_set']
            if not isinstance(usersubscription_set, list):
                usersubscription_set = [usersubscription_set]
            user_subs = PlatformSettingsModels.UserSubscription.objects.filter(
                    id__in = usersubscription_set
                )
            for user_sub in user_subs:
                student_subscription, created = PlatformSettingsModels.StudentSubscription.objects.get_or_create(
                    student = student_instance,
                    user_subscription = user_sub
                )
                if created:
                    if user_sub.studentsubscription_set.all().count() > user_sub.subscription.students_number:
                        student_subscription.delete()
                        student_instance.delete()
                        raise serializers.ValidationError({
                            'detail': 'Maximum number of students reached, you must update your subscription to create new students'})

    def create(self, validated_data):
        
        student_instance = super().create(validated_data)
        self.update_student_user_subscriptions(student_instance, validated_data)
        return student_instance

    def update(self, instance, validated_data):
        student_instance = super().update(instance, validated_data)
        self.update_student_user_subscriptions(student_instance, validated_data)
        return student_instance
