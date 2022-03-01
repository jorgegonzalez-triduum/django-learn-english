import pytz
from django.utils import timezone
from django.contrib.auth.models import User
from triduum_resource.cross_app.serializers import InitHyperlinkedModelSerializer
from platform_settings.models import Subscription, UserSubscription, StudentSubscription, SubscriptionExercise
from rest_framework import serializers
from courses_management.serializers import ExerciseSerializer
from courses_management.models import Exercise
from triduum_resource.cross_app import serializers as base_serializers

class SubscriptionExerciseSerializer(InitHyperlinkedModelSerializer):

    exercise = ExerciseSerializer(fields=['id', 
                            'name', 'url', 'image', 'description', 
                            'video_url', 'icon_name', 'color', 'order', 
                            'level_info', 'exercise_type', 'exercise_type_verbose'], read_only=True)

    class Meta:
        model = SubscriptionExercise
        fields = ['exercise']

class SubscriptionSerializer(InitHyperlinkedModelSerializer):

    exercises_info = SubscriptionExerciseSerializer(source="subscriptionexercise_set", many=True, read_only=True)

    class Meta:
        model = Subscription
        fields = ['url', 'id', 'name',
                'description',
                'students_number',
                'days_term',
                'exercises_info',
                'usersubscription_set',
                'subscriptionexercise_set'
            ]
        extra_kwargs = {
            'usersubscription_set': { 'read_only': True },
            'subscriptionexercise_set': { 'read_only': True }
        }

    def update_subscription_exercise(self, instance, validated_data):
        if 'subscriptionexercise_set' in self.context['request'].data:
            exercises_url_data = self.context['request'].data['subscriptionexercise_set']
            exercises_queryset = Exercise.objects.filter(id__in=exercises_url_data)
            exercises_exist_queryset = SubscriptionExercise.objects.filter(subscription=instance)
            dict_exercises_exist = { x.exercise.id : x for x in exercises_exist_queryset }
            ids_exist_exercises = list(set(exercises_exist_queryset.values_list('exercise__id', flat=True)))
            list_delete_exercise = list(set(ids_exist_exercises) - set(exercises_url_data))
            for exercise in exercises_queryset:
                    subscription_exercise, created = SubscriptionExercise.objects.get_or_create(
                        subscription = instance,
                        exercise = exercise
                    )
            if list_delete_exercise:
                for x in list_delete_exercise:
                    instance_exer = dict_exercises_exist.get(x)
                    if instance_exer:
                        instance_exer.delete()


    def create(self, validated_data):
        subscription_instance = super().create(validated_data)
        self.update_subscription_exercise(subscription_instance, validated_data)
        return subscription_instance

    def update(self, instance, validated_data):
        subscription_instance = super().update(instance, validated_data)
        self.update_subscription_exercise(subscription_instance, validated_data)
        return subscription_instance

class StudentSubscriptionSerializer(InitHyperlinkedModelSerializer):

    class Meta:
        model = StudentSubscription
        fields = ['user_subscription', 'student']
        depth = 1

class UserSubscriptionSerializer(InitHyperlinkedModelSerializer):
    
    subscription_info = SubscriptionSerializer(source='subscription',read_only=True)
    user_info = base_serializers.UserSerializer(source='user', read_only=True,
                    fields=["url", "id", "username", "first_name", "last_name",
                        "email", "is_superuser", "is_active", "user_info"])
    active = serializers.SerializerMethodField()
    format_start = serializers.DateTimeField(source='start_date', format='%Y-%m-%d %H:%M:%S', read_only=True)
    format_end = serializers.DateTimeField(source='end_date', format='%Y-%m-%d %H:%M:%S', read_only=True)
    days = serializers.SerializerMethodField()
    active_students = serializers.SerializerMethodField()
    students_info = StudentSubscriptionSerializer(source="studentsubscription_set", many=True, read_only=True)
    exercises_info = SubscriptionSerializer(source="subscriptionexercise_set", many=True, read_only=True)
    
    class Meta:
        model = UserSubscription
        fields = ['url', 'id', 'user', 'user_info',
            'name',
            'subscription',
            'format_start',
            'format_end',
            'subscription_info',
            'start_date',
            'end_date',
            'active',
            'disabled',
            'days', 
            'active_students',
            'students_info',
            'studentsubscription_set',
            'exercises_info'
        ]
        extra_kwargs = {
            # 'end_date': {'read_only': True},
            'disabled' : {'read_only': True}}
    
    def get_active_students(self, instance):
        return instance.studentsubscription_set.all().count()

    def get_active(self,instance):
        active = False
        if instance.disabled == False:
            if instance.end_date:
                if instance.start_date <= timezone.now() and timezone.now() <= instance.end_date:
                    active = True
            else:
                if timezone.now() >= instance.start_date:
                    active = True
        return active

    def get_days(self, instance):
        seconds = instance.end_date - instance.start_date
        return divmod(seconds.total_seconds(), 86400)[0]

class SubscriptionDetailSerializer(InitHyperlinkedModelSerializer):

    usersubscription_set_info = UserSubscriptionSerializer(source="usersubscription_set",remove_fields=['subscription_info'], read_only=True, many=True)
    # exercises_info = ExerciseSerializer(source="exercises", many=True, read_only=True)

    class Meta:
        model = Subscription
        fields = ['url',  'name',
            'description',
            'students_number',
            'days_term',
            'exercises_info',
            'usersubscription_set',
            'usersubscription_set_info']