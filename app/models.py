from django.db import models
from cloudinary import config as cloudinary_config
from line.cloudinary import set_image_upload
from line.utilities import get_profile


class SfContact(models.Model):
    class Meta:
        db_table = 'contact'

    name = models.CharField(
        max_length=255, null=True, blank=True,
        db_column='name')
    lastname = models.CharField(
        max_length=255, null=True, blank=True,
        db_column='lastname')
    line_id = models.CharField(
        max_length=255, null=True, blank=True,
        db_column='line_id__c')
    image_path = models.CharField(
        max_length=255, null=True, blank=True,
        db_column='image_path__c')
    character_01_ok = models.BooleanField(
        default=False,
        db_column='character_01_ok__c')
    character_02_ok = models.BooleanField(
        default=False,
        db_column='character_02_ok__c')
    character_03_ok = models.BooleanField(
        default=False,
        db_column='character_03_ok__c')
    premium_distribution_ok = models.BooleanField(
        default=False,
        db_column='premium_distribution_ok__c')

    def __str__(self):
        return self.line_id

    @classmethod
    def create(cls, line_id):
        try:
            return cls.objects.get(line_id=line_id)
        except cls.DoesNotExist:
            profile = get_profile(line_id)
            return cls(line_id=line_id,
                       name=profile.display_name,
                       lastname=profile.display_name).save()

    @classmethod
    def get_obj_by_line_id(cls, line_id):
        return cls.objects.filter(line_id=line_id)

    @classmethod
    def get_by_line_id(cls, line_id):
        return cls.objects.filter(line_id=line_id).first()

    @classmethod
    def image_upload_by_line_id(cls, line_id, file, message_id):
        data_obj = cls.objects.filter(line_id=line_id)
        data = data_obj.values().first()

        set_image_upload(file, message_id)

        cloudinary_path = ('https://res.cloudinary.com/' +
                           cloudinary_config().cloud_name + '/image/upload/')

        file_names = data.get('image_path')
        file_name = cloudinary_path + message_id + '.jpg'
        if not file_names:
            update_file = file_name
        else:
            update_file = file_names + '\n' + file_name

        data_obj.update(image_path=update_file)

    def reload(self):
        new_self = self.__class__.objects.get(pk=self.pk)
        self.__dict__.update(new_self.__dict__)

    def update(self, **data):
        self.__class__.objects.filter(pk=self.pk).update(**data)
