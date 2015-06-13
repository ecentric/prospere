from django.test import TestCase
from prospere.lib.test import ExtraTestCase, DocumentTestCase
from django.contrib.auth.models import User
from prospere.contrib.cabinet.models import Storages
from django.core.urlresolvers import reverse
from decimal import Decimal
from prospere.contrib.cabinet.models import Documents
from prospere.contrib.account.models import UserProfiles
from prospere.contrib.account.models import Bookmarks

class Vote(DocumentTestCase):

    def test_naming(self):
        url = reverse('prospere_vote')
        self.assertEqual(url,'/vote/')

    def test_vote_2vote(self):
        response = self.client.post(reverse('prospere_vote'), {"id":self.disseminator_document.id,"score":4.5})
        document = Documents.objects.get(id=self.disseminator_document.id)
        profile = UserProfiles.objects.get(user = self.disseminator)
        self.assertEqual(profile.count_vote, 1)
        self.assertEqual(profile.mark, Decimal("4.5"))
        self.assertEqual(document.count_vote, 1)
        self.assertEqual(document.mark, Decimal("4.5"))
        self.assertEqual(response.content,'{"state": "OK"}')

        response = self.client.post(reverse('prospere_vote'), {"id":self.disseminator_document.id,"score":3})
        document = Documents.objects.get(id=self.disseminator_document.id)
        profile = UserProfiles.objects.get(user = self.disseminator)
        self.assertEqual(profile.count_vote, 1)
        self.assertEqual(profile.mark, Decimal("4.5"))
        self.assertEqual(document.count_vote, 1)
        self.assertEqual(document.mark, Decimal("4.5"))
        self.assertEqual(response.content,'{"state": "ERROR"}')

    def test_vote_without_id_score(self):

        response = self.client.post(reverse('prospere_vote'), {"id":self.disseminator_document.id})
        document = Documents.objects.get(id=self.disseminator_document.id)
        profile = UserProfiles.objects.get(user = self.disseminator)
        self.assertEqual(profile.count_vote, 0)
        self.assertEqual(profile.mark, Decimal("0"))
        self.assertEqual(document.count_vote, 0)
        self.assertEqual(document.mark, Decimal("0"))
        self.assertEqual(response.content,'{"state": "ERROR"}')

        response = self.client.post(reverse('prospere_vote'), {"score":4.5})
        document = Documents.objects.get(id=self.disseminator_document.id)
        profile = UserProfiles.objects.get(user = self.disseminator)
        self.assertEqual(profile.count_vote, 0)
        self.assertEqual(profile.mark, Decimal("0"))
        self.assertEqual(document.count_vote, 0)
        self.assertEqual(document.mark, Decimal("0"))
        self.assertEqual(response.content,'{"state": "ERROR"}')
        
class GetTree(DocumentTestCase):
    '''
    Testing getting document tree, also test getting hidden document
    '''
    def setUp(self):
        DocumentTestCase.setUp(self)
        import os
        dir = os.path.dirname(__file__)
        from django.core.files import File
        file = open(dir+'/for_test/vremena.zip','rb')
        file = File(file)
        self.file = file

        self.hidden_document1 = Documents.objects.create(path = '/'+str(self.disseminator_section.pk)+'/',
                                                              title='title',description='test document',
                                                              user=self.disseminator,file=file,file_size=file.size, 
                                                              storage = self.disseminator_storage)
        self.hidden_document2 = Documents.objects.create(path = '/'+str(self.disseminator_section.pk)+'/',
                                                              title='title',description='test document',
                                                              user=self.disseminator,file=file,file_size=file.size, 
                                                              storage = self.disseminator_storage)
    def tearDown(self):
        DocumentTestCase.tearDown(self)
        self.hidden_document1.delete()
        self.hidden_document2.delete()

    def test_naming(self):
        url = reverse('prospere_get_storage_tree')
        self.assertEqual(url,'/get_storage_tree/')

    def test_getting_disseminator2_storage_tree(self):
        response = self.client.get(reverse('prospere_get_storage_tree'), { "storage_id" : self.disseminator2_storage.id })
        self.failUnless(response.content.count('"mem_busy": ' + str(self.disseminator2_storage.mem_busy)))
        self.failUnless(response.content.count('"id": ' + str(self.d2_section1_0.id)))
        self.failUnless(response.content.count('"id": ' + str(self.disseminator2_document.id)))
        self.failUnless(response.content.count('"id": ' + str(self.disseminator2_section.id)))
        self.failUnless(response.content.count('"is_my_storage": false'))
        self.failUnless(response.content.count('"success": true'))

    def test_getting_my_disseminator_storage_tree(self):
        self.login(username = 'disseminator', password = 'password')
        response = self.client.get(reverse('prospere_get_storage_tree'), { "storage_id" : self.disseminator_storage.id })
        self.failUnless(response.content.count('"mem_busy": ' + str(self.disseminator_storage.mem_busy)))
        self.failUnless(response.content.count('"id": ' + str(self.disseminator_document.id)))
        self.failUnless(response.content.count('"id": ' + str(self.disseminator_section.id)))
        self.failUnless(response.content.count('"id": ' + str(self.section1_0.id)))
        self.failUnless(response.content.count('"id": ' + str(self.section2_0.id)))
        self.failUnless(response.content.count('"id": ' + str(self.section1_1.id)))
        self.failUnless(response.content.count('"id": ' + str(self.section2_1.id)))
        self.failUnless(response.content.count('"id": ' + str(self.hidden_document1.id)))
        self.failUnless(response.content.count('"id": ' + str(self.hidden_document2.id)))
        self.failUnless(response.content.count('"id": ' + str(self.disseminator_document.id)))
        self.failUnless(response.content.count('"is_my_storage": true'))
        self.failUnless(response.content.count('"success": true'))

    def test_getting_disseminator_storage_tree_anonymously(self):
        response = self.client.get(reverse('prospere_get_storage_tree'), { "storage_id" : self.disseminator_storage.id })
        self.failUnless(response.content.count('"mem_busy": ' + str(self.disseminator_storage.mem_busy)))
        self.failUnless(response.content.count('"id": ' + str(self.disseminator_document.id)))
        self.failUnless(response.content.count('"id": ' + str(self.disseminator_section.id)))
        self.failUnless(response.content.count('"id": ' + str(self.section1_0.id)))
        self.failUnless(response.content.count('"id": ' + str(self.section2_0.id)))
        self.failUnless(response.content.count('"id": ' + str(self.section1_1.id)))
        self.failUnless(response.content.count('"id": ' + str(self.section2_1.id)))
        self.failIf(response.content.count('"id": ' + str(self.hidden_document1.id)))
        self.failIf(response.content.count('"id": ' + str(self.hidden_document2.id)))
        self.failUnless(response.content.count('"id": ' + str(self.disseminator_document.id)))
        self.failUnless(response.content.count('"is_my_storage": false'))
        self.failUnless(response.content.count('"success": true'))

    def test_getting_not_my_disseminator_storage_tree(self):
        self.login(username = 'disseminator2', password = 'password')
        response = self.client.get(reverse('prospere_get_storage_tree'), { "storage_id" : self.disseminator_storage.id })
        #import json 
        #self.assertEqual(json.JSONDecoder().decode(response.content), [])
        self.failUnless(response.content.count('"mem_busy": ' + str(self.disseminator_storage.mem_busy)))
        self.failUnless(response.content.count('"id": ' + str(self.disseminator_document.id)))
        self.failUnless(response.content.count('"id": ' + str(self.disseminator_section.id)))
        self.failUnless(response.content.count('"id": ' + str(self.section1_0.id)))
        self.failUnless(response.content.count('"id": ' + str(self.section2_0.id)))
        self.failUnless(response.content.count('"id": ' + str(self.section1_1.id)))
        self.failUnless(response.content.count('"id": ' + str(self.section2_1.id)))
        self.failIf(response.content.count('"id": ' + str(self.hidden_document1.id)))
        self.failIf(response.content.count('"id": ' + str(self.hidden_document2.id)))
        self.failUnless(response.content.count('"id": ' + str(self.disseminator_document.id)))
        self.failUnless(response.content.count('"is_my_storage": false'))
        self.failUnless(response.content.count('"success": true'))

    def test_getting_without_id(self):
        response = self.client.get(reverse('prospere_get_storage_tree'))
        self.assertEqual(response.content,'{\n  "errors": "storage_id missed", \n  "success": false\n}')        

