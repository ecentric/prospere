from django.db import models
from django.conf import settings

import os
from django.utils.encoding import force_unicode, smart_str
import datetime
import random

class DocumentFile(models.FileField):
    '''Document file field'''
    unsafe_ext = ['.exe','.com','.pif','.bat','.scr']
    max_filepath_length = 50
    upload_to = 'document'
    permissions = getattr(settings,'FILE_UPLOAD_PERMISSIONS')

    def __init__(self, verbose_name = None, name = None, upload_to = '', storage = None, **kwargs):
        super(DocumentFile, self).__init__(verbose_name, name, self.upload_to, storage, max_length = self.max_filepath_length)

    def get_directory_name(self):
        interim_dir = "%02x" % random.getrandbits(8)
        file_path = '/'.join([self.upload_to, interim_dir])

        abs_path = '/'.join([settings.MEDIA_ROOT, file_path])
        if not os.path.exists(abs_path):
            os.mkdir(abs_path, self.permissions)

        return os.path.normpath(force_unicode(datetime.datetime.now().strftime(smart_str(file_path))))

    def get_filename(self, filename, is_shared = False):
        path = self.get_directory_name()
        max_filename_length = self.max_filepath_length - len(path) 

        hash = ""
        if not is_shared:
            hash = "_%06x" % random.getrandbits(24)
        filename_length = len(filename) + len(hash)

        name, ext = os.path.splitext(filename)
        if filename_length >= max_filename_length:
            name, ext = os.path.splitext(filename)
            filename = name[0:max_filename_length - len(ext) - len(hash) - 1] + hash + ext
        else: filename = name + hash + ext

        return os.path.normpath(self.storage.get_valid_name(os.path.basename(filename)))

    def generate_filename(self, instance, filename):
        return os.path.join(self.get_directory_name(), self.get_filename(filename, instance.is_shared))
