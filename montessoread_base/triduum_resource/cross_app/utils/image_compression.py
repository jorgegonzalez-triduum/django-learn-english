from django.conf import settings
from django.core.files import File, temp as tempfile
from django.utils.datastructures import MultiValueDict
from PIL import Image

exts = ['jpg', 'png', 'gif', 'bmp', 'jpeg']

def convert_image(name, content, quality = 50):
    if not name.split('.')[-1].lower() in exts: return name, content
    try:
        file_temp = tempfile.NamedTemporaryFile(suffix='.webp', dir=settings.FILE_UPLOAD_TEMP_DIR)
        image = Image.open(content)
        image.save(file_temp.name, 'webp', quality = quality)
        with open(file_temp.name, 'r+b') as f:
            new_content = File(f)
            f.close()
            new_content.open()
            new_name = '{}.webp'.format(name.split('.')[0])
            return new_name, new_content
    except:
        return name, content