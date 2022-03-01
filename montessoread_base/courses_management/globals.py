from collections import namedtuple
from django.utils.translation import gettext as _

AudioDivision = namedtuple(
    'AudioDivision', ['whole_word', 'letter', 'segment']) # Segment = Syllable
audio_division = AudioDivision(1,2,3)


PlayExerciseStatus = namedtuple(
    'PlayExerciseStatus', ['created', 'playing', 'terminated', 'exited'])
play_exercise_status = PlayExerciseStatus(1,2,3, 4)


ExerciseType = namedtuple(
    'ExerciseType', ['pronunciation', 'rhyming_images', 'correct_image', 
                    'rhyming_images_four', 'alphabet_sounds', 'blending', 'blending_basic',
                    'beggining_sounds'],)
exercise_type = ExerciseType((1, _('Pronunciation')), 
                            (2, _('Rhyming images')), 
                            (3, _('Correct image')), 
                            (4, _('Rhyming images (2 - 2)')), 
                            (5, _('Alphabet sounds')),
                            (6, _('Blending')),
                            (7, _('Blending basic')),
                            (8, _('Beggining sounds')))

QualificationType = namedtuple(
    'QualificationType', ['showed', 'practiced', 'master']
)
qualification_type = QualificationType((1, _('Showed')), (2, _('Practiced')), (3, 'Master'))