
from django.db import models
from django.db.models.fields.files import ImageFieldFile
from .utils.image_compression import convert_image

class AutoWebpImageFieldFile(ImageFieldFile):
    def save(self, name, content, save=True):
        name, content = convert_image(name, content)
        name = self.field.generate_filename(self.instance, name)
        self.name = self.storage.save(name, content, max_length=self.field.max_length)
        setattr(self.instance, self.field.name, self.name)
        self._committed = True
        # Save the object because it has changed, unless save is False
        if save:
            self.instance.save()
    save.alters_data = True


class AutoWebpFileField(models.FileField):
    '''
    allows you to pass any file, and if it is an image try to convert it into webp format
    '''
    attr_class = AutoWebpImageFieldFile

    def pre_save(self, model_instance, add):
        file = getattr(model_instance, self.attname)
        if file and not file._committed:
            # Commit the file to storage prior to saving the model
            file.save(file.name, file.file, save=False)
        return file


class AutoWebpImageField(models.ImageField):
    
    attr_class = AutoWebpImageFieldFile

    def pre_save(self, model_instance, add):
        file = getattr(model_instance, self.attname)
        if file and not file._committed:
            # Commit the file to storage prior to saving the model
            file.save(file.name, file.file, save=False)
        return file
