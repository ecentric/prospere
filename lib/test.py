from prospere.contrib.cabinet.models import Documents, Sections, Storages
from prospere.contrib.market.models import Dealings
from django.contrib.auth.models import User
import os
from datetime import datetime
from django.test import TestCase
from operator import attrgetter
from django.core.files import File

from django.conf import settings

settings.MEDIA_ROOT = settings.TEST_MEDIA_ROOT

class ExtraTestCase(TestCase):
    
    def assertQuerysetIdEqual(self, qs, values):
        return self.assertEqual(set(map(attrgetter("id"), qs)), set(values))
    
    def assertGetQuerysetEqual(self,qs,values,getter):
        return self.assertEqual(map(getter, [qs]), values)
        
class DocumentTestCase(ExtraTestCase):

    def login(self,username,password):
        response = self.client.post('/login/',{'username':username,
                                                       'password':password})
        return response
        
    def setUp(self):
        self.user = User.objects.create_user('user','user@email.ru','password')
        self.disseminator = User.objects.create_user('disseminator','disseminator@email.ru','password')
        self.disseminator2 = User.objects.create_user('disseminator2','disseminator2@email.ru','password')  
        self.store_disseminator = User.objects.create_user('store_disseminator','disseminator3@email.ru','password')  
        
        self.disseminator_storage = self.disseminator.storages_set.get()
        self.store_disseminator_storage = self.store_disseminator.storages_set.get()
        self.store_disseminator_storage.is_store = True
        self.store_disseminator_storage.save()
        self.disseminator2_storage = self.disseminator2.storages_set.get()

        self.disseminator_store_section = Sections.objects.create(storage=self.store_disseminator_storage, caption="top_sec")
        self.disseminator_section = Sections.objects.create(storage=self.disseminator_storage, 
                                                            caption="top_section", is_shared = True)
        self.disseminator2_section = Sections.objects.create(storage=self.disseminator2_storage, 
                                                             caption="top_section", is_shared = True)

        # _0 - owner disseminator
        self.section1_0 = Sections.objects.create(storage=self.disseminator_storage, caption="section1_0", is_shared = True)
        self.section2_0 = Sections.objects.create(storage=self.disseminator_storage, caption="section2_0", is_shared = True)
        self.section1_1 = Sections.objects.create(storage=self.disseminator_storage, caption="section1_1", 
                                                  path='/'+str(self.section1_0.pk)+'/', is_shared = True)
        self.section2_1 = Sections.objects.create(storage=self.disseminator_storage, caption="section2_1", 
                                                  path='/'+str(self.section1_0.pk)+'/', is_shared = True)
        # disseminator2
        self.d2_section1_0 = Sections.objects.create(storage=self.disseminator2_storage, caption="d2_section1_0", 
                                                     is_shared = True)

        self.disseminator_profile = self.disseminator.get_profile()

        dir = os.path.dirname(__file__)
        from django.core.files import File
        file = open(dir+'/for_test/vremena.zip','rb')
        file = File(file)
        self.file = file

        self.disseminator_document = Documents.objects.create(path = '/'+str(self.disseminator_section.pk)+'/',
                                                              title='title',description='test document',
                                                              user=self.disseminator,file = file,file_size=file.size, 
                                                              storage = self.disseminator_storage, is_shared = True)

        self.disseminator2_document = Documents.objects.create(path = '/'+str(self.disseminator2_section.pk)+'/',
                                                               title='title2', description='test document2', 
                                                               user=self.disseminator2, file=file,file_size=file.size, 
                                                               storage = self.disseminator2_storage, is_shared = True)

    def tearDown(self):
        self.disseminator_document.file.delete()    
        self.disseminator2_document.file.delete()


class MarketTestCase(DocumentTestCase):
    def setUp(self):
        super(MarketTestCase,self).setUp()

        self.paid_disseminator_document_PD = Documents.objects.create(path = '/'+str(self.disseminator_section.pk)+'/',
                                                                   title='buy me', description='buy me please',
                                                                   user=self.disseminator,
                                                                   file=self.file,file_size=self.file.size, 
                                                                   storage = self.disseminator_storage, 
                                                                   is_free = False, cost = str(10.30))
        self.paid_disseminator_document_BT = Documents.objects.create(path = '/'+str(self.disseminator_section.pk)+'/',
                                                                   title='buy me', description='buy me please',
                                                                   user=self.disseminator,
                                                                   file=self.file,file_size=self.file.size, 
                                                                   storage = self.disseminator_storage, 
                                                                   is_free = False, cost = str(10.30))
        self.paid_disseminator_document_WP = Documents.objects.create(path = '/'+str(self.disseminator_section.pk)+'/',
                                                                   title='buy me', description='buy me please',
                                                                   user=self.disseminator,
                                                                   file=self.file,file_size=self.file.size, 
                                                                   storage = self.disseminator_storage, 
                                                                   is_free = False, cost = str(10.30))

        self.PD_deal = Dealings.objects.create(buyer = self.user, seller = self.disseminator,
                                               product = self.paid_disseminator_document_PD,state = 'PD',
                                               cost = self.paid_disseminator_document_PD.cost, date = datetime.now())
        self.BT_deal = Dealings.objects.create(buyer = self.user, seller = self.disseminator,
                                               product = self.paid_disseminator_document_BT,state = 'BT',
                                               cost = self.paid_disseminator_document_BT.cost, date = datetime.now())
        self.WP_deal = Dealings.objects.create(buyer = self.user, seller = self.disseminator,
                                               product = self.paid_disseminator_document_WP,state = 'WP',
                                               cost = self.paid_disseminator_document_WP.cost, date = datetime.now())

        self.disseminator_BT_deal = Dealings.objects.create(buyer = self.disseminator,
                                    seller = self.disseminator,product = self.paid_disseminator_document_BT,state = 'BT',
                                    cost = self.paid_disseminator_document_BT.cost, date = datetime.now())
        self.disseminator_PD_deal = Dealings.objects.create(buyer = self.disseminator,
                                    seller = self.disseminator,product = self.paid_disseminator_document_PD,state = 'PD',
                                    cost = self.paid_disseminator_document_PD.cost, date = datetime.now())

        self.assertEqual(self.paid_disseminator_document_PD.cost, self.PD_deal.cost)

    def tearDown(self):
        super(MarketTestCase,self).tearDown()
        self.paid_disseminator_document_PD.file.delete()    
        self.paid_disseminator_document_BT.file.delete()
        self.paid_disseminator_document_WP.file.delete()

