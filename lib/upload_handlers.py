import logging

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadhandler import MemoryFileUploadHandler
from django.contrib.sessions.backends.db import SessionStore
import time

class UploadProgressCachedHandler(MemoryFileUploadHandler):
    """
    Tracks progress for file uploads.
    The http post request must contain a query parameter, 'X-Progress-ID',
    which should contain a unique string to identify the upload to be tracked.
    """

    def __init__(self, request=None):
        super(UploadProgressCachedHandler, self).__init__(request)
        self.progress_id = None
        self.cache_key = None

        # update data when received count_chunks_for_update chunks
        self.count_chunks_for_update = 15
        self.update_sec_interval = 1

        self.received_chunks = 0
        self.accounted_chunks = 0
        self.last_update = time.time()

    def handle_raw_input(self, input_data, META, content_length, boundary, encoding=None):
        self.content_length = content_length
        if 'X-Progress-ID' in self.request.GET:
            self.progress_id = self.request.GET['X-Progress-ID']
        if 'HTTP_X_PROGRESS_ID' in self.request.META:
            self.progress_id = self.request.META['HTTP_X_PROGRESS_ID']
        if self.progress_id:
            self.cache_key = "%s_%s" % (self.request.META['REMOTE_ADDR'], self.progress_id )
            try:
                s = SessionStore(session_key = self.request.session.session_key)
            except:
                return None
            s[self.cache_key] = {
                    'state': 'uploading',
                    'size': self.content_length,
                    'received': 0
                }
            s.save()
        return None

    def new_file(self, field_name, file_name, content_type, content_length, charset=None):
        pass

    def receive_data_chunk(self, raw_data, start):
        self.received_chunks += 1
        time.sleep(0.1)
        timestamp = time.time()
        if (self.cache_key and (timestamp - self.last_update > self.update_sec_interval) 
                          and (self.received_chunks - self.accounted_chunks > self.count_chunks_for_update)):
            self.last_update = timestamp
            self.accounted_chunks = self.received_chunks
            try:
                s = SessionStore(session_key = self.request.session.session_key)
            except:
                return None
            data = s[self.cache_key]
            data['received'] = self.received_chunks*self.chunk_size
            s.save()
        return raw_data
    
    def file_complete(self, file_size):
        pass

    def upload_complete(self):
        if self.cache_key:
            try:
                s = SessionStore(session_key = self.request.session.session_key)
            except:
                return None
            data = s[self.cache_key]
            data['state'] = 'done'
            s.save()

