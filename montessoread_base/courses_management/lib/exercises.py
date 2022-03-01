from courses_management import globals as choices

definitions = {
    choices.exercise_type.pronunciation[0]: {
        'simultaneous_images': 0, # 1 or 2
        'time_between_image_and_name': 0, # in ms
        'number_of_images_to_display': 0, # < to number of selected materials
        'random' : None, # Random image sorting
        'autoplay': None, # True False
        'time_between_slides': None, #If autoplay is True
        'is_it_qualified': None, #is it qualified?
        'show_label': True, #show the image name?
        'materials': []
    },
    choices.exercise_type.rhyming_images[0]:{
        'number_of_images_that_rhyme': 0, # 2 or 3
        'time_between_image_and_name': 0, # in ms
        'number_of_images_to_display': 0, # < to number of selected materials
        'show_label': True,  #show the image name?
        'random' : False, # Random image sorting
        'materials': []
    },
    choices.exercise_type.alphabet_sounds[0]:{
        'reproduction_quantity': 1, # 2 or 3
        'time_between_image_and_name': 0, # in ms
        'number_of_images_to_display': 1, # < to number of selected materials
        'show_label': True,  #show the image name?
        'autoplay': True,
        'random' : True, # Random image sorting
        'materials': []
    },
    choices.exercise_type.blending[0]:{
        'number_of_images_to_display': 1, # < to number of selected materials
        'show_label': False,  #show the image name?
        'random' : True, # Random image sorting
        'materials': [],
        'time_between_sounds': 1000,
        'microphone_required': True
    },
    choices.exercise_type.blending_basic[0]:{
        "random": True,
        "autoplay": False,
        "simultaneous_images": 1,
        "time_between_slides": 6000,
        "time_between_sounds": 1000,
        "time_between_letters": 2000,
        'microphone_required': False
    },
    choices.exercise_type.beggining_sounds[0]:{
        "random": True,
        "autoplay": False,
        'show_label': False
    }
}


def make_init_definition(exercise_type):
    #Expects an exercise model instance
    return definitions[exercise_type]