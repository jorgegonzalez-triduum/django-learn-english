from django.urls import path, include
from rest_framework import routers
from .views_api import (category, 
                        alphabet,
                        object,
                        audiofile,
                        section,
                        level,
                        exercise,
                        play_exercise,
                        play_exercise_try,
                        play_exercise_status,
                        play_exercise_result,
                        qualification_teacher)

router = routers.DefaultRouter()
router.register(r'category', category.CategoryViewSet)
router.register(r'alphabet', alphabet.AlphabetViewSet)
router.register(r'object', object.ObjectViewSet)
router.register(r'audiofile', audiofile.AudioFileViewSet)
router.register(r'section', section.SectionViewSet)
router.register(r'level', level.LevelViewSet)
router.register(r'exercise', exercise.ExerciseViewSet)
router.register(r'play_exercise', play_exercise.PlayExerciseViewSet)
router.register(r'play_exercise_try', play_exercise_try.PlayExerciseTryViewSet)
router.register(r'play_exercise_status', play_exercise_status.PlayExerciseStatusViewSet)
router.register(r'play_exercise_results', play_exercise_result.PlayExerciseResultViewSet)
router.register(r'qualification_teacher', qualification_teacher.QualificationTeacherVs)

urlpatterns = [
    path('', include(router.urls)),
]