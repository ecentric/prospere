from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

def create_profile(sender,**kwargs):
    if kwargs['created']:
        UserProfiles.objects.create(user = kwargs['instance'])
models.signals.post_save.connect(create_profile,sender = User)

class UserProfiles(models.Model):
    user = models.ForeignKey(User, unique=True)

    description = models.TextField()
	
    picture = models.ImageField(upload_to='picture', blank=True)
    small_picture = models.ImageField(upload_to='picture', blank=True)

    count_vote = models.IntegerField(default=0)
    mark = models.DecimalField(max_digits=2, decimal_places=1, default=Decimal("0.0"))

    document_notif_on = models.BooleanField(default = True)

    default_picture = 'picture/unknown.jpg'
    default_small_picture = 'picture/unknown_small.jpg'	

    @staticmethod
    def get_image_url(image_field, default_picture):
        if image_field == '':
		    return image_field.storage.url(default_picture)
        else:
            if image_field.storage.exists(image_field.name):
                return image_field.url
            else:
                import logging
                logger = logging.getLogger('log')
                logger.error('User picture does not exist %s' % (image_field.name) )
                return image_field.storage.url(default_picture)

    def get_picture_url(self):
        return UserProfiles.get_image_url(self.picture,self.default_picture)
		
    def get_small_picture_url(self):
        return UserProfiles.get_image_url(self.small_picture,self.default_small_picture)

    def delete_small_picture(self):
        if self.small_picture.name !='' and self.small_picture.storage.exists(self.small_picture.name):
            self.small_picture.storage.delete(self.small_picture.name)

    def delete_picture(self):
        if self.picture.name !='' and self.picture.storage.exists(self.picture.name):
            self.picture.storage.delete(self.picture.name)

    def __unicode__(self):
        return str(self.user)

bookmark_choices = (
        ('UR', 'User'),
)
class Bookmarks(models.Model):
    user = models.ForeignKey(User)

    type = models.CharField(max_length=2, choices=bookmark_choices)
    object = models.IntegerField()

    class Meta:
        unique_together = ('user', 'type', 'object',)

