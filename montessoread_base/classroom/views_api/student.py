from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from courses_management.permissions import HasSubscriptionOrIsAdmin
from classroom.models import Student
from triduum_resource.cross_app.views_api.base import BaseModelViewSet
from classroom import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView, status
from courses_management import serializers as courses_serializers
from courses_management import models as courses_models
from courses_management import globals as courses_globals

class StudentViewSet(BaseModelViewSet):

    permission_classes_custom = [IsAuthenticated, HasSubscriptionOrIsAdmin]
    
    permission_classes_by_action = {
        'create': permission_classes_custom,
        'list': permission_classes_custom,
        'retrieve': permission_classes_custom,
        'update': permission_classes_custom,
        'destroy': permission_classes_custom,
        'get_student_exercise_grades': permission_classes_custom
    }

    queryset = Student.objects.all()
    serializer_class = serializers.StudentSerializer
    search_fields = ['name', 'gender', 'surname', 'birth_date',
                'studentsubscription__user_subscription__user__username',
                'studentsubscription__user_subscription__name',
                'studentsubscription__user_subscription__user__first_name',
                'studentsubscription__user_subscription__user__last_name',
                'studentsubscription__user_subscription__user__email']

    ordering = ['-studentsubscription']

    def get_queryset(self):
        if self.user_subscription_instance:
            return self.user_subscription_instance.students.all()
        else:
            return Student.objects.all()

    @action(detail=True, methods=['get'])
    def get_student_exercise_grades(self, request, pk):
        student = self.get_object()
        user = request.user
        data = {
            'student': self.serializer_class(instance=student, context={
                'request': request
                }).data,
            'exercises': [],
            'tries_column_number': 0
        }
        if self.user_subscription_instance and not user.is_superuser:
            exercises = self.user_subscription_instance.subscription.subscriptionexercise_set.all().values_list('exercise__id', flat=True)
            exercises = courses_models.Exercise.objects.filter(id__in = exercises)
        else:
            exercises = courses_models.Exercise.objects.all()
        exercises = exercises.order_by('order')
        data['exercises'] = courses_serializers.ExerciseSerializer(
            instance=exercises, 
            fields=['url', 'id', 'name'],
            many=True, context={
            'request': request
            }).data
        
        tries_column_number = int(request.data.get('tries_column_number', 10))
        for exercise in data['exercises']:
            play_exercise_tries = courses_models.PlayExerciseTry.objects.prefetch_related(
                'playexerciseresult_set').filter(
                play_exercise__student = student,
                play_exercise__exercise__id = exercise['id'],
                playexercisestatus__status = courses_globals.play_exercise_status.terminated
                ).order_by('-id')
            exercise['times'] = play_exercise_tries.count()
            play_exercise_tries_to_show = play_exercise_tries[:tries_column_number]
            exercise['tries_info'] = []
            qualification_teacher = courses_models.QualificationTeacherExercise.objects.select_related(
                                        'exercise', 'student').filter(student=student, exercise__id = exercise['id']).last()
            exercise['qualification_teacher'] = ''
            exercises_dict = { x.id: x for x in exercises }
            if qualification_teacher:
                exercise['qualification_teacher'] = qualification_teacher.qualification
                
            for pe_try in play_exercise_tries_to_show:
                result =  pe_try.playexerciseresult_set.all().last()
                exercise['tries_info'].append({
                    'id': pe_try.id if result else '',
                    'try': pe_try.try_number,
                    'id_result': result.id if result else '',
                    'result': result.qualification if result else '',
                    'result_display': result.get_qualification_display() if result else '',
                    'result_date': result.meta['created_at'] if result else ''
                })
        max_tries_columns = max([x['times'] for x in data['exercises']])
        if max_tries_columns < tries_column_number:
            tries_column_number = max_tries_columns
        data['tries_column_number'] = tries_column_number
        exercises_for_section = {}
        for exercise in data['exercises']:
            data_exercise = exercises_dict.get(exercise['id'])
            for col in range(0, tries_column_number):
                exercise['try_{}'.format(
                    str(col)
                )] = exercise['tries_info'][col][
                    'result_display'] if (col + 1) <= len(exercise['tries_info']) else ''
            if data_exercise.level.section.id in exercises_for_section:
                exercises_for_section[data_exercise.level.section.id].append(exercise)
            else:
                exercises_for_section.update({ data_exercise.level.section.id: [ exercise ] })

        sections = courses_models.Section.objects.filter(
                        id__in=exercises.values_list('level__section', flat=True)
                    )
        sections_data = courses_serializers.SectionSerializer(
                    sections.order_by('order'), many=True,
                    context={'request':request}
                ).data
        for section in sections_data:
            section['data_exercises'] = exercises_for_section.get(section['id'])
        return Response({ 'sections': sections_data, 
                'tries_column_number': data['tries_column_number'],
                'student': data['student']
            })