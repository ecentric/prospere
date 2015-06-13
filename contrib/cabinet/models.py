from django.db import models
from djangosphinx import SphinxSearch
from django.conf import settings
from django.contrib.auth.models import User
from tinymce import models as tinymce_models
import logging
from fields import DocumentFile

from decimal import Decimal
import os
import random

from django.conf import settings
max_depth = getattr(settings,'MAX_PATH_DEPTH')

class Storages(models.Model):

    user = models.ForeignKey(User)
    mem_limit = models.IntegerField(default = 209715200)
    mem_busy = models.IntegerField(default = 0)
    title = models.CharField(max_length = 20, default = "")
    is_store = models.BooleanField(default = False)

    def update_fields(self, **kwargs):
        self.objects.filter(pk=self.pk).update(**kwargs)
    update_fields.alters_data = True

    def __unicode__(self):
        return str(self.user)

    class Meta:
        verbose_name = 'storage'
        verbose_name_plural = 'storages'

class StorageBans(models.Model):

    storage = models.ForeignKey(Storages)
    creation_date = models.DateTimeField(auto_now_add = True)
    is_processed = models.BooleanField()
    amount_of_ban = models.IntegerField()

class PublicSectionManager(models.Manager):

    def get_query_set(self):
        return super(PublicSectionManager,self).get_query_set().filter(is_shared = True)

class Sections(models.Model):

    storage = models.ForeignKey(Storages)
    caption = models.CharField(max_length = 30)
    path = models.CharField(max_length = (max_depth - 1) * 19 + 5, default = '/', db_index = True)
    is_shared = models.BooleanField(default = False)

    public_objects = PublicSectionManager()
    objects = models.Manager()

    def share(self):
        self.is_shared = True
        self.save()

    def hide(self):
        self.is_shared = False
        self.save()        

    def __unicode__(self):
        return self.caption

class PublicDocumentManager(models.Manager):

    def get_query_set(self):
        return super(PublicDocumentManager,self).get_query_set().filter(is_removed = False, is_shared = True)

class NoRemovedDocumentManager(models.Manager):

    def get_query_set(self):
        return super(NoRemovedDocumentManager,self).get_query_set().filter(is_removed = False)

DOCUMENT_DESCRIPTION_MAX_LENGTH = getattr(settings,'DOCUMENT_DESCRIPTION_MAX_LENGTH', 3000)

class Documents(models.Model):

    path = models.CharField(max_length = max_depth * 19 + 5, db_index = True)
    title = models.CharField(max_length = 30)
    description = models.TextField(max_length=DOCUMENT_DESCRIPTION_MAX_LENGTH)
    html_description = tinymce_models.HTMLField(max_length=DOCUMENT_DESCRIPTION_MAX_LENGTH)
    
    file = DocumentFile()
    file_size = models.IntegerField()
	
    user = models.ForeignKey(User)
    storage = models.ForeignKey(Storages)

    is_removed = models.BooleanField(default=False)
    is_moderated   = models.BooleanField(default=False)
    is_shared = models.BooleanField(default = False)
    is_free = models.BooleanField(default=True)

    last_purchase = models.DateTimeField(default=None, blank=True, null=True)

    cost = models.DecimalField(max_digits=6, decimal_places=2, default = Decimal("0.00"))

    creation_date = models.DateTimeField(auto_now_add = True)
    
    count_vote = models.IntegerField(default = 0)
    mark = models.DecimalField(max_digits = 2, decimal_places = 1, default = Decimal("0.0"))

    # WARNING you maust use public user when don't need hidden files
    objects = NoRemovedDocumentManager()
    public_objects = PublicDocumentManager()
    all_objects = models.Manager()

    def hide_file(self, save = True):
        if not self.file.storage.exists(self.file.name): return
        filename = self.file.file.name
        self.file.file.close()
        hash = "_%06x" % random.getrandbits(24)
        name, ext = os.path.splitext(filename)
        available_filename = self.file.storage.get_available_name(name + hash + ext)
        os.rename(filename, available_filename)
        self.file.name = available_filename[available_filename.rindex(DocumentFile.upload_to):]
        if save: self.save()

    def share_file(self, save = True):
        if not self.file.storage.exists(self.file.name): return
        filename = self.file.file.name
        self.file.file.close()
        name, ext = os.path.splitext(filename)
        try:
            name = name[:name.rindex('_')]
        except ValueError:
            logger = logging.getLogger('log')
            logger.error("Warning - share file name don't contain hash")
            return;
        available_filename = self.file.storage.get_available_name(name + ext)
        os.rename(filename, available_filename)
        self.file.name = available_filename[available_filename.rindex(DocumentFile.upload_to):]
        if save: self.save()

    def delete_file(self):
        if self.file.name !='' and self.file.storage.exists(self.file.name):
            self.file.storage.delete(self.file.name)
        
    def delete(self, request = None):
        self.delete_file()
        document_id = self.id
        models.Model.delete(self)

        from signals import document_deleted
        document_deleted.send(sender = None, document_id = document_id )

    def get_file_url(self):
        logger = logging.getLogger('log')
        if self.file.name == '':
            logger.error('Document (id - %s) file name is empty.' % (self.pk) )
            return None
        else:
            if self.file.storage.exists(self.file.name):
                return self.file.url
            else:
                logger.error('Document (id - %s) file does not exist %s' % (self.pk, self.file.name) )
                return None

    search = SphinxSearch(
           index ='document_search', 
           weights = { # individual field weighting
               'title': 100,
               'description': 50,
           }
       )

    def share(self, save = True):
        self.share_file(save = False)
        self.is_shared = True
        if save: self.save()   

    def hide(self, save = True):
        self.hide_file(save = False)
        self.is_shared = False
        if save: self.save()   

    def __unicode__(self):
        return self.title

def create_storage(sender,**kwargs):
    if kwargs['created']:
        Storages.objects.create(user = kwargs['instance'])
models.signals.post_save.connect(create_storage,sender = User)

def increase_storage_mem_busy(sender,**kwargs):
    if kwargs['created']:
        storage = kwargs['instance'].storage
        storage.mem_busy += kwargs['instance'].file_size
        storage.save()
models.signals.post_save.connect(increase_storage_mem_busy, sender = Documents)

def decrease_storage_mem_busy(sender,**kwargs):
    storage = kwargs['instance'].storage
    storage.mem_busy -= kwargs['instance'].file_size
    storage.save()
models.signals.post_delete.connect(decrease_storage_mem_busy, sender = Documents)

