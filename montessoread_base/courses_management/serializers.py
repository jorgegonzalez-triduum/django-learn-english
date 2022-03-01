from django.db.models import Case, IntegerField, When
from triduum_resource.cross_app.serializers import InitHyperlinkedModelSerializer
from courses_management.models import (
    Category, AudioFile, Alphabet, Object, Section,
    Level, Exercise, PlayExercise, PlayExerciseStatus,
    PlayExerciseTry, PlayExerciseResult, QualificationTeacherExercise)
from courses_management import globals as choices
from rest_framework import serializers
from classroom.models import Student


class CategoryImageSerializer(InitHyperlinkedModelSerializer):

    class Meta:
        model = Category
        fields = ['url', 'image']

class CategorySerializerBase(InitHyperlinkedModelSerializer):

    parent_tree = serializers.SerializerMethodField()
    audiofiles = serializers.SerializerMethodField()
    countmaterials = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['url', 'id','meta', 'parent', 'name', 'description', 'icon_name',
                'color', 'image', 'order', 'hover_text', 'audiofiles', 'countmaterials',
                'parent_tree']
        extra_kwargs = {
            'meta': {'read_only': True},
            'image': {'read_only': True}
            }
        
    def get_parent_tree(self,instance):
        return {}
    
    def get_countmaterials(self, instance):
        materials = Object.objects.filter(category_id=instance.id, disabled=False).count()
        return materials

    def get_audiofiles(self, instance):
        audiofiles = AudioFile.objects.filter(model=1, related_id=instance.id)
        return AudioFileSerializer(
            audiofiles, many=True, context={
                'request': self.context['request']
            }, read_only=True).data
        
    def create(self, validated_data):
        try:
            instance = super().create(validated_data)
        except Exception as e:
            raise serializers.ValidationError({
                'detail': e
            })
        return instance

    def update(self, isntance, validated_data):
        try:
            instance = super().update(isntance, validated_data)
        except Exception as e:
            raise serializers.ValidationError({
                'detail': e
            })
        return instance


class CategorySerializer(CategorySerializerBase):
    
    parent_tree = CategorySerializerBase(source="get_parent_tree",
        read_only=True, many=True,
        fields=['url', 'name'])

class AlphabetForAudioSerializer(InitHyperlinkedModelSerializer):

    audiofiles = serializers.SerializerMethodField()
    
    class Meta:
        model = Alphabet
        fields = [
                'url',
                'id',
                'letter',
                'audiofiles']

    def get_audiofiles(self, instance):
        audiofiles = AudioFile.objects.filter(model=0, related_id=instance.id)
        return AudioFileSerializer(
            audiofiles, many=True, context={
                'request': self.context['request']
            }, read_only=True).data

class AudioFileSerializer(InitHyperlinkedModelSerializer):
    
    alphabet_info = AlphabetForAudioSerializer(source="alphabet", read_only=True)

    class Meta:
        model = AudioFile
        fields = ['url', 'id', 'model', 'related_id', 'value', 'division', 'file', 'alphabet', 'alphabet_info', 'order']

class AlphabetSerializer(InitHyperlinkedModelSerializer):
    audiofiles = serializers.SerializerMethodField()
    class Meta:
        model = Alphabet
        fields = [
                'url',
                'id',
                'order',
                'letter',
                'pronunciation',
                'image',
                'audiofiles']

    def get_audiofiles(self, instance):
        audiofiles = AudioFile.objects.filter(model=0, related_id=instance.id)
        return AudioFileSerializer(
            audiofiles, many=True, context={
                'request': self.context['request']
            }, read_only=True).data


class ObjectSerializer(InitHyperlinkedModelSerializer):

    audiofiles = serializers.SerializerMethodField()
    audio_files = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_info = CategorySerializer(
        source='category', read_only=True)
    play_ready = serializers.SerializerMethodField()
    
    class Meta:
        model = Object
        fields = [
                'url',
                'id',
                'meta',
                'category',
                'category_name',
                'category_info',
                'name',
                'description',
                'icon_name',
                'image',
                'audiofiles',
                'audio_files', # New audiofiles with categories
                'play_ready']
        extra_kwargs = {
            'meta': {'read_only': True},
            'image': {'read_only': True},
            }

    def get_audiofiles(self, instance):
        audiofiles = AudioFile.objects.filter(model=2, related_id=instance.id)
        return AudioFileSerializer(
            audiofiles, many=True, context={
                'request': self.context['request']
            }, read_only=True).data
        
    def get_audio_files(self, instance):
        response = {}
        for choice in choices.audio_division:
            audiofiles = AudioFile.objects.filter(
                    model=2,
                    related_id=instance.id,
                    division=choice).order_by('order')
            response.update({
                choice : AudioFileSerializer(
                            audiofiles, many=True, context={
                                'request': self.context['request']
                            }, read_only=True).data
            })
        return response              

    def get_play_ready(self, instance):
        play_ready = False
        if instance.image and AudioFile.objects.filter(
            model=2,
            related_id=instance.id,
            division=choices.audio_division.whole_word).exists():
            play_ready = True
        return play_ready
    

class ObjectImageSerializer(InitHyperlinkedModelSerializer):

    class Meta:
        model = Object
        fields = ['url', 'image']


class SectionSerializer(InitHyperlinkedModelSerializer):

    levels_count = serializers.SerializerMethodField()
    exercises_count = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = ['url', 'id',
                'name', 'description', 'video_url','icon_name', 'order', 'image', 'level_set', 'levels_count', 'exercises_count']

        extra_kwargs = {
            'meta': {'read_only': True},
            'image': {'read_only': True},
            'level_set': {'read_only': True},
            }

    def get_levels_count(self, instance):
        return instance.level_set.all().count()

    def get_exercises_count(self, instance):
        i = 0
        for lv in instance.level_set.all():
            i += lv.exercise_set.all().count()
        return i

class SectionImageSerializer(InitHyperlinkedModelSerializer):

    class Meta:
        model = Section
        fields = ['url', 'image']


class LevelSerializer(InitHyperlinkedModelSerializer):

    section_info = SectionSerializer(source='section', read_only=True)
    exercises_count = serializers.SerializerMethodField()

    class Meta:
        model = Level
        fields = ['url', 'id', 'section', 
                    'name', 'description', 'image', 'section_info', 'icon_name', 'order', 'exercises_count']
        extra_kwargs = {
            'meta': {'read_only': True},
            'image': {'read_only': True},
            }

    def get_exercises_count(self, instance):
        return instance.exercise_set.all().count()

class LevelImageSerializer(InitHyperlinkedModelSerializer):

    class Meta:
        model = Level
        fields = ['url', 'image']


class ExerciseSerializer(InitHyperlinkedModelSerializer):

    level_info = LevelSerializer(source='level', read_only=True)
    exercise_type_verbose = serializers.CharField(source='get_exercise_type_display', read_only=True)
    definition = serializers.SerializerMethodField()
    
    class Meta:
        model = Exercise
        fields = ['url', 'id', 'meta', 'level', 'level_info', 'exercise_type', 'exercise_type_verbose',
                    'name', 'description', 'video_url','icon_name', 'color', 'order', 'image', 'definition']
        extra_kwargs = {
            'meta': {'read_only': True},
            'image': {'read_only': True},
            'definition': {'read_only': True},
            }

    def get_definition(self, instance):
        
        data = instance.definition
        list_exercise_type = [choices.exercise_type.pronunciation[0], 
                            choices.exercise_type.correct_image[0],
                            choices.exercise_type.rhyming_images_four[0], 
                            choices.exercise_type.alphabet_sounds[0],
                            choices.exercise_type.blending[0],
                            choices.exercise_type.blending_basic[0],
                            choices.exercise_type.beggining_sounds[0]]
        if instance.exercise_type in list_exercise_type:
            if 'materials' in data and data['materials']:
                try:
                    materials = data['materials']
                except:
                    pass
                if isinstance(materials, int):
                    list_materials = data['materials']
                    data['materials'] = ObjectSerializer(
                        Object.objects.filter(id__in = data['materials']),
                            many=True,context={
                        'request': self.context['request']
                    }).data
                    data['list_materials'] = list_materials
                elif isinstance(materials, list):
                    ids_materials = []
                    list_materials = data['materials']
                    for val in data['materials']:
                        if isinstance(val, list):
                            for ids_m in val:
                                if isinstance(ids_m, list):
                                    ids_materials.extend([ x for x in ids_m ])
                                else:
                                    ids_materials.append(ids_m)        
                        else:
                            ids_materials.append(val)    

                    # custom ordering (from list)
                    cases = [When(pk=pk, then=sort_order) for sort_order, pk in enumerate(ids_materials)]
                    objects = Object.objects.filter(id__in = ids_materials).annotate(
                                sort_order=Case(*cases, output_field=IntegerField())
                                ).order_by('sort_order')

                    data['materials'] = ObjectSerializer(
                        objects,
                            many=True,context={
                        'request': self.context['request']
                    }).data
                    data['list_materials'] = list_materials

        if instance.exercise_type == choices.exercise_type.rhyming_images[0]:
            if 'materials' in data and data['materials']:
                try:
                    materials = data['materials']
                except:
                    pass
                if isinstance(materials, int):
                    data['materials'] = ObjectSerializer(
                        Object.objects.filter(id__in = data['materials']),
                            many=True,context={
                        'request': self.context['request']
                    }).data
                elif isinstance(materials, list):
                    ids_materials = []
                    list_materials = data['materials']
                    for arr in data['materials']:
                        if isinstance(arr, list):
                            for arr2 in arr:
                                if isinstance(arr2, list):
                                    for x in arr2:
                                        ids_materials.append(x)
                                else:
                                    ids_materials.append(arr2)
                        else: 
                            ids_materials.append(arr)
                        #ids_materials.extend([ x for x in arr ])
                    data['materials'] = ObjectSerializer(
                        Object.objects.filter(id__in = ids_materials),
                            many=True,context={
                        'request': self.context['request']
                    }).data
                    data['list_materials'] = list_materials

        return data


class ExerciseSerializerLite(InitHyperlinkedModelSerializer):

    level_info = LevelSerializer(source='level', read_only=True)
    exercise_type_verbose = serializers.CharField(source='get_exercise_type_display',read_only=True)
    
    class Meta:
        model = Exercise
        fields = ['url', 'id', 'meta', 'level', 'level_info', 'exercise_type', 'exercise_type_verbose',
                    'name', 'description', 'video_url','icon_name', 'color', 'order', 'image', 'definition']
        extra_kwargs = {
            'meta': {'read_only': True},
            'image': {'read_only': True},
            'definition': {'read_only': True},
            }


class ExerciseDefinitionSerializer(InitHyperlinkedModelSerializer):
    
    class Meta:
        model = Exercise
        fields = ['url', 'id','exercise_type', 'definition']

class ExerciseImageSerializer(InitHyperlinkedModelSerializer):

    class Meta:
        model = Exercise
        fields = ['url', 'image']



class PlayExerciseStatusSerializer(InitHyperlinkedModelSerializer):

    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = PlayExerciseStatus
        fields = ['id', 'url', 'meta', 
            'play_exercise_try', 
            'status', 'status_display']
        extra_kwargs = {
            'meta': {'read_only': True},
            }

class PlayExerciseResultSerializer(InitHyperlinkedModelSerializer):

    result_display = serializers.CharField(source='get_result_display', read_only=True)
    
    class Meta:
        model = PlayExerciseResult
        fields = ['id', 'url', 'meta', 'play_exercise_try',
            'result_display',
            'running_definition']
        extra_kwargs = {
            'meta': {'read_only': True},
            }

    def create(self, validated_data):
        data_request = self.initial_data
        if 'data_qualification' in data_request and data_request['data_qualification']:
            if 'qualification_no_interactive' in data_request['data_qualification']:
                validated_data['qualification'] = choices.qualification_type.showed[0]
                validated_data['running_definition'] = data_request['data_qualification']['qualification_no_interactive']
            else:
                try_number_data = validated_data['play_exercise_try']
                if try_number_data:
                    if try_number_data.try_number == 1:
                        validated_data['qualification'] = choices.qualification_type.showed[0]
                    else:
                        if 'error' in data_request['data_qualification'] and data_request['data_qualification']['error']:
                            validated_data['qualification'] = choices.qualification_type.practiced[0]
                        else:
                            validated_data['qualification'] = choices.qualification_type.master[0]
                    validated_data['running_definition'] = data_request['data_qualification'] 
        try:
            inst_playexercise = super().create(validated_data)
        except Exception as e:
            raise serializers.ValidationError({
                'detail': e
            })
        return inst_playexercise


class PlayExerciseTrySerializer(InitHyperlinkedModelSerializer):

    playexerciseresult_set_info = PlayExerciseResultSerializer(source='playexerciseresult_set', many=True, read_only=True)
    playexercisestatus_set_info = PlayExerciseStatusSerializer(source='playexercisestatus_set', many=True, read_only=True)
    
    class Meta:
        model = PlayExerciseTry
        fields = ['id', 'url', 'meta', 'play_exercise',
            'try_number', 'playexerciseresult_set', 
            'playexerciseresult_set_info', 'playexercisestatus_set', 
            'playexercisestatus_set_info',
            ]
        extra_kwargs = {
            'meta': {'read_only': True},
            'playexerciseresult_set': {'read_only': True, 'required': False},
            'playexercisestatus_set': {'read_only': True, 'required': False},
        }



class StudentSerializer(InitHyperlinkedModelSerializer):
    
    '''
    Original serializer is placed in classroom.serializers...
    '''
    
    full_name = serializers.SerializerMethodField()
    gender_display = serializers.CharField(source="get_gender_display", required=False)

    class Meta:
        model = Student
        fields = [
            'url', 'full_name', 'name', 'surname', 'gender',
            'gender_display', 'birth_date']

    def get_full_name(self, instance):
        return f"{instance.name} {instance.surname}".strip()
    

class PlayExerciseSerializer(InitHyperlinkedModelSerializer):

    status = serializers.SerializerMethodField()
    exercise_info = ExerciseSerializer(source='exercise', read_only=True)
    student_info = StudentSerializer(source='student', read_only=True)
    playexercisetry_set_info = PlayExerciseTrySerializer(source='playexercisetry_set', many=True, read_only=True)
    
    class Meta:
        model = PlayExercise
        fields = ['url', 'id', 'meta', 'exercise', 'exercise_info',
                    'playexercisetry_set','playexercisetry_set_info', 'status', 'student', 'student_info']
        extra_kwargs = {
            'meta': {'read_only': True},
            'playexercisetry_set': {'read_only': True},
            'exercise_info': {'read_only': True}
            }

    def create(self, validated_data):
        play_exercise_inst = PlayExercise.objects.filter(
                                    exercise=validated_data['exercise'], 
                                    student=validated_data['student']).last()
        if not play_exercise_inst:
            try:
                play_exercise_inst = super().create(validated_data)
            except Exception as e:
                raise serializers.ValidationError({
                    'detail': e
                })
        play_exercise = PlayExerciseSerializer(instance=play_exercise_inst, 
                                context={'request': self.context['request'] }).data
        instance_playtry = PlayExerciseTry.objects.filter(play_exercise=play_exercise_inst).last()
        if not instance_playtry:
            try:
                instance_playtry = PlayExerciseTrySerializer(data={
                            'play_exercise': play_exercise['url'],
                            'try_number': 1 },
                            context={'request': self.context['request'] })
                if instance_playtry.is_valid():
                    instance_playtry.save()
                else:
                    raise Exception('Ocurrio un error al crear el intento')
            except Exception as e:
                raise serializers.ValidationError({
                    'detail': e
                })
        else:
            try_play = PlayExerciseTrySerializer(
                            data={ 
                                'play_exercise': play_exercise['url'], 
                                'try_number': instance_playtry.try_number + 1 
                            },
                            context={'request': self.context['request'] })
            try:
                if try_play.is_valid():
                    try_play.save()
            except Exception:                
                raise serializers.ValidationError({
                    'detail': 'Ocurrio un error al crear el intento'
                })
        return play_exercise
    
    def get_status(self, instance):
        data = {}
        p_e_try = instance.playexercisetry_set.all().last()
        if p_e_try:
            status = p_e_try.playexercisestatus_set.all().last()
            if status:
                data = PlayExerciseStatusSerializer(
                    instance = status,
                    context={
                    'request': self.context['request']
                }).data
        return data


class QualificationTeacherSerializer(InitHyperlinkedModelSerializer):

    class Meta:
        model = QualificationTeacherExercise
        fields = ['exercise', 'student', 'qualification']