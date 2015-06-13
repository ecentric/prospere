from prospere.lib.test import ExtraTestCase, DocumentTestCase
from prospere.contrib.cabinet.forms import AddDocumentForm, EditDocumentForm, AddSectionForm
from prospere.contrib.cabinet.models import Documents, Sections, Storages, StorageBans
from prospere.contrib.comment.models import Comments
from prospere.contrib.market.models import Dealings
from django.contrib.auth.models import User
from prospere.contrib.account.models import Bookmarks

from django.contrib.sessions.models import Session
from django.contrib.contenttypes.models import ContentType
from prospere.copia.models import SessionBonds

from prospere.copia.signal_handlers import *
import os
from django.core.files import File

from operator import attrgetter

class cabinet(DocumentTestCase):    

    def setUp(self):
        DocumentTestCase.setUp(self)

        ctype = ContentType.objects.get_for_model(Documents)
        
        Comments.objects.create(content_type = ctype,object_pk = self.disseminator_document.id, 
                                        name = '', user_id = self.user.id, comment='comment')

    def test_password_changed(self):
        self.login(username = "user", password = "password")
        password_changed(None, self.user.id)
        bond = SessionBonds.objects.get(user = self.user.id)
        count = Session.objects.filter(session_key = bond.session_key).count()
        self.assertEqual(count,0)

    def test_deleting_comments(self):
        delete_comment(None, self.disseminator_document.id)
        count = Comments.objects.all().count()
        self.assertEqual(count,0)

    def test_deleting_comments_with_document(self):
        self.disseminator_document.delete()
        count = Comments.objects.all().count()
        self.assertEqual(count,0)


