from django.db import models
import datetime
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from triduum_resource.cross_app.models import Base
from triduum_resource.cross_app import fields as self_fields
from courses_management import globals as choices
from django.contrib.postgres.fields import JSONField, ArrayField
from courses_management.lib.exercises import make_init_definition
from classroom.models import Student

class Category(Base):
    
    clear_cache = True

    parent = models.ForeignKey(_('Category'), on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(_('Name'), max_length=150)
    description = models.TextField(null=True, blank=True)
    icon_name = models.CharField(_('Icon name'), max_length=80, null=True, blank=True)
    color = models.CharField(_('Color'), max_length=20, null=True, blank=True)
    image = self_fields.AutoWebpFileField(upload_to='category/images/',
            verbose_name='_(Category image)', null=True, blank=True
            )
    order = models.PositiveSmallIntegerField(_('Order'), default=1)
    hover_text = models.CharField(_('Hover text'), max_length=1300, null=True, blank=True)

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
        if self.parent:
            if self.parent.id == self.id:
                raise ValidationError(
                    _("You cannot relate a category to itself")
                    )
        if len(self.get_parent_tree()) > 3:
            raise ValidationError(
                _("You cannot create more than 3 levels in a category")
                )
        return super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['disabled', 'name'],
                name="unique_together_category")
        ]



class Language(Base):

    name = models.CharField(_('Language'), max_length=30)
    short_name = models.CharField(_('Short name'), max_length=6)
    
    def __str__(self):
        return '{} ({})'.format(str(self.name), str(self.short_name))

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['disabled', 'name', 'short_name'],
                name="unique_together_language")
        ]

    #INSERT INTO courses_management_language (id, meta, disabled, "name", short_name) VALUES (1, '{}', false, 'English', 'en');
    #INSERT INTO courses_management_language (id, meta, disabled, "name", short_name) VALUES (2, '{}', false, 'Spanish', 'es');



class Alphabet(Base):

    clear_cache = True

    # language = models.ForeignKey(_('Language'), on_delete=models.CASCADE, default="en-US")
    order = models.PositiveSmallIntegerField(_('Order'), default=1)
    letter = models.CharField(_('Letter'), max_length=10)
    pronunciation = models.CharField(_('Pronunciation'), max_length=10)
    image = self_fields.AutoWebpFileField(upload_to='alphabeth/images/',
            verbose_name='_(Letter image)', null=True, blank=True
            )

    def __str__(self):
        return str(self.letter)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['disabled', 'language', 'letter'], #todo: order?
                name="unique_together_alphabet")
        ]

def directory_path_audio(instance, filename):
    filename = '{}.{:%d%m%Y}.{}'.format(instance.related_id, datetime.datetime.now(), filename.split('.')[-1].lower())
    return '{}/audiofile/{}'.format(instance.model, filename)

class AudioFile(Base):
    
    MODELS = [
        (0, _('Alphabet')),
        (1, _('Category')),
        (2, _('Object')),
    ]
    
    AUDIO_DIVISION_CHOICES = (
        (choices.audio_division.whole_word, _('The whole word')),
        (choices.audio_division.letter, _('Letter')),
        (choices.audio_division.segment, _('Segment'))
    )
    
    model = models.IntegerField(choices=MODELS, default=0)
    related_id = models.IntegerField(_('Related id'), default=0)
    order = models.PositiveSmallIntegerField(_('Order'), default=1)
    value = models.CharField(_("Value"),max_length=200, null=True, blank=True)
    division = models.IntegerField(
        _('Audio Division'), choices=AUDIO_DIVISION_CHOICES, default=choices.audio_division.whole_word)
    file = models.FileField(upload_to=directory_path_audio,
            verbose_name='_(Audio file)', null=True, blank=True
            )
    alphabet = models.ForeignKey(Alphabet, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.file and not self.alphabet:
            raise Exception("No file or alphabet supplied") 
        if not self.id:
            if self.division == choices.audio_division.whole_word:
                [x.disable() for x in AudioFile.objects.filter(
                    model=self.model,
                    related_id=self.related_id,
                    division=choices.audio_division.whole_word)]
            # elif self.division == choices.audio_division.letter:
            #     [x.disable() for x in AudioFile.objects.filter(
            #         model=self.model,
            #         related_id=self.related_id,
            #         value=self.value,
            #         division=choices.audio_division.letter)]
            elif self.division == choices.audio_division.segment:
                [x.disable() for x in AudioFile.objects.filter(
                    model=self.model,
                    related_id=self.related_id,
                    value=self.value,
                    division=choices.audio_division.segment)]
            related_id_files = AudioFile.objects.filter(
                model=self.model,
                related_id=self.related_id,
                division=choices.audio_division.letter
            )
            if related_id_files:
                self.order = max(list(related_id_files.values_list('order', flat=True))) + 1
        else:
            if not 'auto_ordering' in kwargs:
                before_instance = AudioFile.objects.get(id=self.id)
                if before_instance.order != self.order:
                    if self.order > before_instance.order:
                        related_id_files = AudioFile.objects.filter(
                            model=self.model,
                            related_id=self.related_id,
                            division=choices.audio_division.letter,
                            order__gte=self.order
                        ).exclude(id=self.id).order_by('order')
                        related_instances = [x for x in related_id_files]
                        for related_instance in related_instances:
                            if related_instance.order == self.order:
                                related_instance.order -= 1
                            related_instance.save(**{'auto_ordering': True})
                    else:
                        related_id_files = AudioFile.objects.filter(
                            model=self.model,
                            related_id=self.related_id,
                            division=choices.audio_division.letter,
                            order__lte=self.order
                        ).exclude(id=self.id).order_by('order')
                        related_instances = [x for x in related_id_files]
                        for related_instance in related_instances:
                            if related_instance.order == self.order:
                                related_instance.order += 1
                                related_instance.save(**{'auto_ordering': True})
                if before_instance.disabled != self.disabled:
                    related_id_files = AudioFile.objects.filter(
                        model=self.model,
                        related_id=self.related_id,
                        division=choices.audio_division.letter,
                        order__gte=self.order
                    ).exclude(id=self.id).order_by('order')
                    related_instances = [x for x in related_id_files]
                    for related_instance in related_instances:
                        related_instance.order -= 1
                        related_instance.save(**{'auto_ordering': True})
            else:
                kwargs.pop('auto_ordering')
        return super().save(*args, **kwargs)
    
    def __str__(self):
        model = self.get_model_display()
        related_id = self.related_id
        if model == 'Alphabet':
            object = Alphabet.objects.filter(id=related_id).last()
        elif model == 'Category':
            object = Category.objects.filter(id=related_id).last()
        elif model == 'Object':
            object = Object.objects.filter(id=related_id).last()
        return '{} - {}'.format(str(model), str(object))

class Object(Base):

    category = models.ForeignKey(_('Category'), on_delete=models.CASCADE)
    name = models.CharField(_('Name'), max_length=150)
    description = models.TextField(null=True, blank=True)
    icon_name = models.CharField(_('Icon name'), max_length=80, null=True, blank=True)
    image = self_fields.AutoWebpFileField(upload_to='object/images/',
            verbose_name='_(Category image)', null=True, blank=True
            )

    def __str__(self):
        return '{} - {}'.format(str(self.category.name), str(self.name))

    def save(self, *args, **kwargs):
        if self.id and self.name != Object.objects.get(id=self.id).name:
            [x.disable() for x in AudioFile.objects.filter(
                model=2,
                related_id=self.id,
                division=choices.audio_division.letter)]
        return super().save(*args, **kwargs)

class Section(Base):
    name = models.CharField(_('Name'), max_length=250)
    description = models.TextField(null=True, blank=True)
    icon_name = models.CharField(_('Icon name'), max_length=80, null=True, blank=True)
    order = models.PositiveSmallIntegerField(_('Order'), default=1)
    image = self_fields.AutoWebpFileField(upload_to='courses_management/sections/',
            verbose_name='_(Category image)', null=True, blank=True
            )
    video_url = models.CharField(_('Url'), max_length=250, blank=True, null=True)
    
class Level(Base):
    
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    name = models.CharField(_('Name'), max_length=250)
    description = models.TextField(null=True, blank=True)
    icon_name = models.CharField(_('Icon name'), max_length=80, null=True, blank=True)
    order = models.PositiveSmallIntegerField(_('Order'), default=1)
    image = self_fields.AutoWebpFileField(upload_to='courses_management/level/',
            verbose_name='_(Category image)', null=True, blank=True
            )

class Exercise(Base):
    
    EXERCISE_TYPE_CHOICES = (
        (choices.exercise_type.pronunciation[0], choices.exercise_type.pronunciation[1]),
        (choices.exercise_type.rhyming_images[0], choices.exercise_type.rhyming_images[1]),
        (choices.exercise_type.correct_image[0], choices.exercise_type.correct_image[1]),
        (choices.exercise_type.rhyming_images_four[0], choices.exercise_type.rhyming_images_four[1]),
        (choices.exercise_type.alphabet_sounds[0], choices.exercise_type.alphabet_sounds[1]),
        (choices.exercise_type.blending[0], choices.exercise_type.blending[1]),
        (choices.exercise_type.blending_basic[0], choices.exercise_type.blending_basic[1]),
        (choices.exercise_type.beggining_sounds[0], choices.exercise_type.beggining_sounds[1]),
    )
    
    
    
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    name = models.CharField(_('Name'), max_length=250)
    description = models.TextField(null=True, blank=True)
    color = models.CharField(_('Color'), max_length=20, null=True, blank=True)
    icon_name = models.CharField(_('Icon name'), max_length=80, null=True, blank=True)
    order = models.PositiveSmallIntegerField(_('Order'), default=1)
    image = self_fields.AutoWebpFileField(upload_to='courses_management/exercise/',
            verbose_name='_(Category image)', null=True, blank=True
            )
    video_url = models.CharField(_('Url'), max_length=250, blank=True, null=True)
    exercise_type = models.PositiveIntegerField(
        _('Exercise type'), choices=EXERCISE_TYPE_CHOICES, default=choices.exercise_type.pronunciation[0])
    definition = JSONField(_('Definition'), default=dict)

    def save(self, *args, **kwargs):
        if not self.id:
            self.definition = make_init_definition(self.exercise_type)
        return super().save(*args, **kwargs)

class PlayExercise(Base):
    
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    student  = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        creation =  False
        if not self.id:
            creation = True
        super_save = super().save(*args, **kwargs)
        if creation:
            pass
            # existing_try = PlayExerciseTry.objects.create(
            #     play_exercise=self,
            #     try_number=1)
        return super_save


class QualificationTeacherExercise(Base):

    QUALIFICATION_CHOICES = (
        (choices.qualification_type.showed[0], choices.qualification_type.showed[1]),
        (choices.qualification_type.practiced[0], choices.qualification_type.practiced[1]),
        (choices.qualification_type.master[0], choices.qualification_type.master[1]),
    )

    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="exercise")
    student  = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True, null=True)
    qualification = models.PositiveSmallIntegerField(_('Qualification exercise'), choices=QUALIFICATION_CHOICES)

    def __str__(self):
        return '{} - {}'.format(str(self.exercise.id), str(self.student.id))

    def save(self, *args, **kwargs):
        QualificationTeacherExercise.objects.filter(
                exercise = self.exercise, student = self.student
            ).update(disabled=True)
        super().save(*args, **kwargs)


class PlayExerciseTry(Base):
    
    '''
    Final score:
    
    Se sugiere la letra mas alta de todos los try de el playexercise, sin embargo
    el teacher podrá definir cual es la nota final a su gusto.
    '''
    play_exercise = models.ForeignKey(PlayExercise, on_delete=models.CASCADE)
    try_number = models.PositiveSmallIntegerField(_('Try number'))
    
    def save(self, *args, **kwargs):
        creation =  False
        if not self.id:
            creation = True
        super_save = super().save(*args, **kwargs)
        if creation:
            existing_status = PlayExerciseStatus.objects.create(
                play_exercise_try=self,
                status=choices.play_exercise_status.created)
        return super_save
class PlayExerciseStatus(Base):
    
    
    PLAY_EXERCISE_STATUS = (
        (choices.play_exercise_status.created, _('Created')),
        (choices.play_exercise_status.playing, _('Playing')),
        (choices.play_exercise_status.terminated, _('Terminated')),
        (choices.play_exercise_status.exited, _('Exited')),
    )
    
    play_exercise_try = models.ForeignKey(PlayExerciseTry, on_delete=models.CASCADE, null=True, blank=False)
    status = models.PositiveSmallIntegerField(_('Status'), choices=PLAY_EXERCISE_STATUS)

    def save(self, *args, **kwargs):
        if not self.id:
            existing_status = PlayExerciseStatus.objects.filter(
                play_exercise_try=self.play_exercise_try)
            if existing_status:
                if existing_status.last().status == choices.play_exercise_status.terminated:
                    new_try = PlayExerciseTry()
                    new_try.play_exercise = self.play_exercise_try.play_exercise
                    new_try.try_number = self.play_exercise_try.try_number + 1
                    new_try.save()
                    return new_try.playexercisestatus_set.all().last()
                else:
                    [x.disable() for x in existing_status]
        return super().save(*args, **kwargs)

class PlayExerciseResult(Base):
    
    
    QUALIFICATION_CHOICES = (
        (choices.qualification_type.showed[0], choices.qualification_type.showed[1]),
        (choices.qualification_type.practiced[0], choices.qualification_type.practiced[1]),
        (choices.qualification_type.master[0], choices.qualification_type.master[1]),
    )
    '''
    Posibles notas: [
        1: S,
        2: P,
        3: M
    ]
    
    Calificación del try:
    
    Si el play_exercise_try == 1: nota siempre va a ser S
    Si el play_exercise_try >= 2: si se equivoco en una imagen(Paso) del ejercio de una queda en P
    Si saco todas buenas quedo en M.
    
    La nota final que se mostrará en la tabla de estudiantes va a ser la nota mas alta alcanzada.
    Esta nota la puede modificar el profesor.
    
    Campos:
    notas = [{'group_material': 1, 'calificacion': 'Mala'}
    {'group_material': 2}, 'calificacion': 'Mala'}
    ,]
    contador de buenas (Materiales)
    contador de malas (Materiales)
    total de materiales: 
    
    Calificación del try.
    
    '''
    play_exercise_try = models.ForeignKey(PlayExerciseTry, on_delete=models.CASCADE)
    qualification = models.PositiveSmallIntegerField(_('Qualification'), choices=QUALIFICATION_CHOICES)
    running_definition =  JSONField(_('Running definition'), default=dict)

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

