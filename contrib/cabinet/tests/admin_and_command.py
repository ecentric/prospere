from prospere.lib.test import ExtraTestCase, DocumentTestCase
from prospere.contrib.cabinet.forms import AddDocumentForm, EditDocumentForm, AddSectionForm
from prospere.contrib.cabinet.models import Documents, Sections, Storages, StorageBans
from prospere.contrib.market.models import Dealings
from django.contrib.auth.models import User
from prospere.contrib.cabinet.management.commands.check_storage_bans import Command
from prospere.contrib.cabinet.management.commands.check_storages_mem_busy import Command as StoragesBusyCommand

from prospere.contrib.cabinet.admin import DocumentsAdmin
import os
from django.core.files import File

from operator import attrgetter

class admin(DocumentTestCase):    

    def setUp(self):
        DocumentTestCase.setUp(self)
        self.document_actions = DocumentsAdmin(Documents,"")
        self.queryset_ids = [self.disseminator_document.id, self.disseminator2_document.id]
        self.queryset = Documents.all_objects.filter(id__in = self.queryset_ids)

        dir = os.path.dirname(__file__)
        file = open(dir+'/for_test/file2','rb')
        file = File(file)
        self.some_document = Documents.all_objects.create(path = '/'+str(self.disseminator_section.pk)+'/',
                                                              title='title',description='test document',
                                                              user=self.disseminator,file=file,file_size=file.size, 
                                                              storage = self.disseminator_storage)
        self.user.is_superuser = True
        class Request():
            user = None
        self.request =  Request()
        self.request.user = self.user
        self.user.save()

    def tearDown(self):
        DocumentTestCase.tearDown(self)
        self.some_document.delete()

    def test_setting_moderated(self):
        response = self.login(username='user',password='password')
        self.document_actions.set_moderated(self.request, self.queryset)
        document = Documents.all_objects.filter(id__in = self.queryset_ids)
        self.assertEqual(document[0].is_moderated, True)
        self.assertEqual(document[1].is_moderated, True)
        self.assertEqual(self.some_document.is_moderated, False)

    def check_deleting(self):
        count = Documents.all_objects.filter(id__in = self.queryset_ids).count()
        self.assertEqual(count, 0)
        count = Documents.all_objects.all().count()
        self.assertEqual(count, 1)

    def test_deleting_document(self):
        response = self.login(username='user',password='password')
        self.document_actions.delete(self.request, self.queryset)
        self.check_deleting()

    def test_delete_and_add_ban(self):
        response = self.login(username='user',password='password')
        storage = Storages.objects.get(id = self.disseminator_document.storage_id)
        storage.mem_limit = 20
        storage.save()
        old_mem_limit2 = Storages.objects.get(id = self.disseminator2_document.storage_id).mem_limit
        self.document_actions.delete_and_add_ban(self.request, self.queryset)
        self.check_deleting()

        ban = StorageBans.objects.get(storage = self.disseminator_document.storage_id)
        storage = Storages.objects.get(id = ban.storage_id)
        self.assertEqual(ban.amount_of_ban, 20)
        self.assertEqual(storage.mem_limit, 0)

        ban = StorageBans.objects.get(storage = self.disseminator2_document.storage_id)
        storage = Storages.objects.get(id = ban.storage_id)
        self.assertEqual(storage.mem_limit, old_mem_limit2 - ban.amount_of_ban)

    def test_change_password_and_delete(self):
        response = self.login(username='user',password='password')
        self.document_actions.change_password_and_delete(self.request, self.queryset)
        self.check_deleting()
        self.disseminator = User.objects.get(id = self.disseminator.id)
        self.failIf(self.disseminator.check_password('password'))
        self.disseminator2 = User.objects.get(id = self.disseminator2.id)
        self.failIf(self.disseminator2.check_password('password'))

class BansCommand(DocumentTestCase):

    def setUp(self):
        DocumentTestCase.setUp(self)
        self.mem_lim1 = storage = Storages.objects.get(id = self.disseminator_storage.id).mem_limit
        self.mem_lim2 = storage = Storages.objects.get(id = self.disseminator2_storage.id).mem_limit
        self.dis1_ban = StorageBans.objects.create(storage = self.disseminator_storage, amount_of_ban = 20, 
                                                                                        is_processed = True)
        self.dis1_ban2 = StorageBans.objects.create(storage = self.disseminator_storage, amount_of_ban = 60,
                                                                                        is_processed = True)
        self.dis2_ban = StorageBans.objects.create(storage = self.disseminator2_storage, amount_of_ban = 34,
                                                                                        is_processed = True)

    def test_check_storage_bans(self):
        com = Command()
        com.BAN_DAYS = 5
        com.handle_noargs()
        count = StorageBans.objects.all().count()
        self.assertEqual(count,3)
        storage = Storages.objects.get(id = self.disseminator_storage.id)
        self.assertEqual(storage.mem_limit, self.mem_lim1)

        storage = Storages.objects.get(id = self.disseminator2_storage.id)
        self.assertEqual(storage.mem_limit,self.mem_lim2)

        com.BAN_DAYS = 0
        com.handle_noargs()
        count = StorageBans.objects.all().count()
        self.assertEqual(count,0)
        storage = Storages.objects.get(id = self.disseminator_storage.id)
        self.assertEqual(storage.mem_limit, self.mem_lim1 + 80)

        storage = Storages.objects.get(id = self.disseminator2_storage.id)
        self.assertEqual(storage.mem_limit,self.mem_lim2 + 34)

class TestStoragesBusyCommand(DocumentTestCase):

    def setUp(self):
        DocumentTestCase.setUp(self)
        self.disseminator_storage.mem_busy = 12
        self.disseminator_storage.save()
        self.disseminator2_storage.mem_busy = 12
        self.disseminator2_storage.save()

    def test_check_storages_busy(self):
        com = StoragesBusyCommand()
        com.handle_noargs()
        storage = self.disseminator.storages_set.get()
        self.assertEqual(storage.mem_busy, self.disseminator_document.file_size)
        self.assertEqual(storage.mem_busy, self.disseminator2_document.file_size)

