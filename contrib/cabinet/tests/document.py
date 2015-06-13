from prospere.lib.test import ExtraTestCase, DocumentTestCase
from prospere.contrib.cabinet.forms import AddDocumentForm, EditDocumentForm, AddSectionForm
from prospere.contrib.cabinet.models import Documents, Sections, Storages
from prospere.contrib.market.models import Dealings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
import os
from django.core.files import File
from django.db.models import Q
from django.utils.html import strip_tags
import json
from operator import attrgetter

class PageAddDocument(DocumentTestCase):           

    def test_getting_add_document_page_with_disseminator(self):
        self.login(username='disseminator',password='password')
        response = self.client.get('/cabinet/add_document/' + str(self.disseminator_section.pk) + '/')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'add_document.html')
        
        self.failUnless(isinstance(response.context['form'],AddDocumentForm))
        form = response.context['form']
        self.assertEqual( (form['title'].value(),form['html_description'].value()),
                          ('', ''))        

    def test_getting_add_document_page_with_disseminator_not_own_section(self):
        self.login(username='disseminator',password='password')
        response = self.client.get('/cabinet/add_document/' + str(self.disseminator2_section.pk) + '/')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'error.html')      
    '''
    test get with anonymous user
    '''  
    def test_getting_add_document_page_with_anonymous_user(self):
        response = self.client.get('/cabinet/add_document/' + str(self.disseminator_section.pk) + '/')
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,'/login/?next=/cabinet/add_document/' + str(self.disseminator_section.pk) + '/') 
 
class ActionAddDocument(DocumentTestCase):

    def test_adiition_document_with_file_size_more_memlimit(self):
        dir = os.path.dirname(__file__)
        file = open(dir+'/for_test/file2','rb')
        file = File(file)
        self.disseminator_storage.mem_limit = self.disseminator_document.file_size + file.size - 1
        self.disseminator_storage.save()
        self.login(username='disseminator',password='password')

        post_form = {'title':'new title',
                     'description':'new my document',
                     'file': file,
                     'is_free': True}
        response = self.client.post('/cabinet/add_document/' + str(self.disseminator_section.pk) + '/',post_form)
        count = Documents.all_objects.filter(user=self.disseminator).count()
        self.assertEqual(count,1)
        storage = self.disseminator.storages_set.get()
        self.assertEqual(storage.mem_busy,self.disseminator_document.file_size)
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'add_document.html')

    def test_adiition_paid_document_empty_cost(self):
        dir = os.path.dirname(__file__)
        file = open(dir+'/for_test/file2','rb')
        file = File(file)
        self.disseminator_storage.mem_limit = self.disseminator_document.file_size + file.size - 1
        self.disseminator_storage.save()
        self.login(username='disseminator',password='password')

        post_form = {'title':'new title',
                     'description':'new my document',
                     'file': file,
                     'is_free': False,
                     'cost' : ''}
        response = self.client.post('/cabinet/add_document/' + str(self.disseminator_section.pk) + '/',post_form)
        count = Documents.all_objects.filter(user=self.disseminator).count()
        self.assertEqual(count,1)
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'add_document.html')

    def test_addition_document_wrong_type(self):
        dir = os.path.dirname(__file__)
        file = open(dir+'/for_test/file.BAt','rb')
        file = File(file)
        self.login(username='disseminator',password='password')

        post_form = {'title':'Bat file',
                     'html_description':'<p>new <B>my</B> document</p>',
                     'file': file,
                     'is_free': True}
        response = self.client.post('/cabinet/add_document/' + str(self.disseminator_section.pk) + '/',post_form)
       
        count = Documents.all_objects.filter(title="Bat file").count()
        self.assertEqual(count,1)

    def test_addition_free_document(self):
        dir = os.path.dirname(__file__)
        file = open(dir+'/for_test/file2','rb')
        file = File(file)
        self.disseminator_storage.mem_limit = self.disseminator_document.file_size + file.size
        self.disseminator_storage.save()
        self.login(username='disseminator',password='password')

        post_form = {'title':'new title',
                     'html_description':'<p>new <B>my</B> document</p>',
                     'file': file,
                     'is_free': True}
        response = self.client.post('/cabinet/add_document/' + str(self.disseminator_section.pk) + 
                                    '/?next=/user/'+self.disseminator.username+'/',post_form)
        value =    [( '/'+str(self.disseminator_section.pk)+'/',
                      post_form['title'],       #title
                      post_form['html_description'], #description
                      strip_tags(post_form['html_description']),
                      self.disseminator_storage, #storage
                      file.size,                        #size of file
                      post_form['is_free'],
                   )]
        document = Documents.all_objects.exclude(Q(pk=self.disseminator_document.pk)|Q(pk=self.disseminator2_document.pk))
        self.assertQuerysetEqual(document,value,
                                 attrgetter("path","title","html_description","description","storage","file_size","is_free"))
        storage = self.disseminator.storages_set.get()
        self.assertEqual(storage.mem_busy,file.size+self.disseminator_document.file_size)
        self.failUnless(document[0].file.storage.exists(document[0].file.name))
        self.assertRedirects(response,'/user/'+self.disseminator.username+'/?message=cabinet_document_saved')
        document[0].file.delete()
        document[0].delete()

    def test_addition_paid_document_to_not_store_storage(self):
        dir = os.path.dirname(__file__)
        file = open(dir+'/for_test/file2','rb')
        file = File(file)
        self.disseminator_storage.mem_limit = self.disseminator_document.file_size + file.size
        self.disseminator_storage.save()
        self.login(username='disseminator',password='password')

        post_form = {'title':'new title',
                     'html_description':'<p>new my document</p>',
                     'file': file,
                     'is_free': False,
                     'cost' : str(10.30)}
        url = reverse("prospere_add_document", kwargs={'section' : self.disseminator_section.pk})
        response = self.client.post(url + '?next=' + url,post_form)
        from decimal import Decimal
        value =    [( '/'+str(self.disseminator_section.pk)+'/',
                      post_form['title'],       #title
                      post_form['html_description'], #description
                      strip_tags(post_form['html_description']),
                      self.disseminator_storage, #storage
                      file.size,                        #size of file
                      True,
                      Decimal('0.00'),
                   )]
        document = Documents.all_objects.exclude(Q(pk=self.disseminator_document.pk) | Q(pk=self.disseminator2_document.pk))
        self.assertQuerysetEqual(document,value,
                                 attrgetter("path", "title", "html_description", "description", "storage", 
                                            "file_size", "is_free","cost"))
        storage = self.disseminator.storages_set.get()
        self.assertEqual(storage.mem_busy,file.size+self.disseminator_document.file_size)
        self.failUnless(document[0].file.storage.exists(document[0].file.name))
        #redirecting
        self.assertRedirects(response, url + '?message=cabinet_document_saved')
        document[0].file.delete()
        document[0].delete()

    def test_addition_paid_document_to_store_storage(self):
        dir = os.path.dirname(__file__)
        file = open(dir+'/for_test/file2','rb')
        file = File(file)
        self.store_disseminator_storage.mem_limit = self.disseminator_document.file_size + file.size
        self.store_disseminator_storage.save()
        self.login(username='store_disseminator',password='password')

        post_form = {'title':'new title',
                     'html_description':'new my document',
                     'file': file,
                     'is_free': False,
                     'cost' : '10.30'}
        url = reverse("prospere_add_document", kwargs={'section' : self.disseminator_store_section.pk})
        response = self.client.post(url + '?next=' + url,post_form)
        from decimal import Decimal
        value =    [( '/'+str(self.disseminator_store_section.pk)+'/',
                      post_form['title'],       #title
                      post_form['html_description'], #description
                      self.store_disseminator_storage, #storage
                      file.size,                        #size of file
                      post_form['is_free'],
                      Decimal(post_form['cost']),
                   )]
        document = Documents.all_objects.exclude(Q(pk=self.disseminator_document.pk)|Q(pk=self.disseminator2_document.pk))
        self.assertQuerysetEqual(document,value,
                                 attrgetter("path","title","html_description","storage","file_size","is_free","cost"))
        storage = self.store_disseminator.storages_set.get()
        self.assertEqual(storage.mem_busy,file.size)
        self.failUnless(document[0].file.storage.exists(document[0].file.name))
        #redirecting
        self.assertRedirects(response, url + '?message=cabinet_document_saved')
        document[0].file.delete()
        document[0].delete()

    def test_addition_document_to_not_own_section(self):
        dir = os.path.dirname(__file__)
        file = open(dir+'/for_test/file2','rb')
        file = File(file)
        self.login(username='disseminator',password='password')

        post_form = {'title':'new title',
                     'html_description':'new my document',
                     'file': file,
                     'is_free': True}
        response = self.client.post('/cabinet/add_document/' + str(self.disseminator2_section.pk) + '/',post_form)
        count = Documents.all_objects.filter(user=self.disseminator2).count()
        self.assertEqual(count,1)
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'error.html')
       
class PageEditingDocument(DocumentTestCase):
     
    def test_getting_edit_document_page_with_disseminator_own_document(self):
        self.login(username='disseminator',password='password')
        response = response = self.client.get('/cabinet/edit_document/'+str(self.disseminator_document.id)+'/')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'edit_document.html')
        
        self.failUnless(isinstance(response.context['form'],EditDocumentForm))
        #self.failUnless(response.context['file_not_requred'])

        form = response.context['form']
        self.assertGetQuerysetEqual(self.disseminator_document,[(form['title'].value(), form['html_description'].value())],
                                    attrgetter("title","html_description"))


    def test_getting_edit_document_page_with_disseminator_not_own_document(self):
        self.login(username='disseminator',password='password')
        response = self.client.get('/cabinet/edit_document/'+str(self.disseminator2_document.id)+'/')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'error.html')
    '''
    test get with anonymous user
    '''     
    def test_getting_edit_document_page_with_anonymous(self):
        response = self.client.get('/cabinet/edit_document/'+str(self.disseminator_document.id)+'/')
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,'/login/?next=/cabinet/edit_document/'+str(self.disseminator_document.id)+'/') 

class ActionEditDocument(DocumentTestCase):
    '''
    test add user views with disseminator user
    '''      
    def test_saving_own_document_file_size_more_limit(self):
        dir = os.path.dirname(__file__)
        file = open(dir+'/for_test/file2','rb')
        file = File(file)
        self.disseminator_storage.mem_limit = file.size -1
        self.disseminator_storage.save()
        self.login(username='disseminator',password='password')

        post_form = {'title' : 'registration',
                     'description' : 'dgjango-registration document',
                     'file' : file}
        
        response = self.client.post('/cabinet/edit_document/'+str(self.disseminator_document.id)+'/',post_form)        
        self.failUnless(response.context['form'].errors['file'])
        count = Documents.all_objects.filter(user=self.disseminator).count()
        self.assertEqual(count,1)
        storage = self.disseminator.storages_set.get()
        self.assertEqual(storage.mem_busy,self.disseminator_document.file_size)            
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'edit_document.html')
    
    def test_saving_free_own_document_with_edit_document_page(self):
        dir = os.path.dirname(__file__)
        from django.core.files import File
        file = open(dir+'/for_test/file2','rb')
        file = File(file)
        self.disseminator_storage.mem_limit = file.size
        self.disseminator_storage.save()
        self.login(username='disseminator',password='password')
        post_form = {'title' : 'registration',
                     'html_description' : '<B>dgjango</B>-registration document',
                     'file' : file}
        url = reverse("prospere_edit_document", kwargs={'document_id' : self.disseminator_document.id})
        response = self.client.post(url + '?next=' + url,post_form)
        value =    [( self.disseminator_document.path,
                      post_form['title'],       #title
                      post_form['html_description'], #description
                      strip_tags(post_form['html_description']),
                      file.size,
                   )]
        document = Documents.all_objects.get(pk = self.disseminator_document.pk)             
        self.assertQuerysetEqual([document],value,
                                 attrgetter("path","title","html_description","description","file_size"))
        #storage = self.disseminator.storages_set.get()
        storage = Storages.objects.get(user = self.disseminator)
        self.assertRedirects(response, url + '?message=cabinet_document_saved')
        self.assertEqual(storage.mem_busy, file.size)                                 
        self.disseminator_document = document

    def test_saving_paid_own_document_with_edit_document_page(self):
        dir = os.path.dirname(__file__)
        from django.core.files import File
        file = open(dir+'/for_test/file2','rb')
        file = File(file)
        self.disseminator_storage.mem_limit = file.size+self.file.size
        self.disseminator_storage.save()
        self.disseminator_paid_document = Documents.all_objects.create(path = '/'+str(self.disseminator_section.pk)+'/',
                                                              title='title',description='test document',
                                                              user=self.store_disseminator,file=self.file,
                                                              file_size=self.file.size, 
                                                              storage = self.store_disseminator_storage,
                                                              cost = "10.40", is_free = False)
        self.login(username='store_disseminator',password='password')
        post_form = {'title' : 'registration',
                     'html_description' : 'dgjango-registration document',
                     'file' : file,
                     'cost' : '20.10'}

        url = reverse("prospere_edit_document", kwargs={'document_id' : self.disseminator_paid_document.id})
        response = self.client.post(url + '?next=' + url,post_form)
        from decimal import Decimal
        value =    [( self.disseminator_paid_document.path,
                      post_form['title'],       #title
                      post_form['html_description'], #description
                      self.file.size,
                      Decimal(post_form['cost'])
                   )]
        document = Documents.all_objects.get(pk = self.disseminator_paid_document.pk)             
        self.assertQuerysetEqual([document],value, attrgetter("path","title","html_description","file_size","cost"))                           
        self.assertRedirects(response, url + '?message=cabinet_document_saved')
        self.disseminator_paid_document.delete()

    def test_replace_file(self):
        self.login(username='disseminator',password='password')
        dir = os.path.dirname(__file__)
        file = open(dir+'/for_test/vremena.zip','rb')
        post_form = {'title' : 'registration',
                     'html_description' : 'dgjango-registration document',
                     'file':file }
        response = self.client.post('/cabinet/edit_document/'+str(self.disseminator_document.id)+'/',post_form)      
        file.close()
        
        document = Documents.all_objects.get(pk=self.disseminator_document.pk)
        old_file = document.file.name
        self.failUnless(self.disseminator_document.file.storage.exists(old_file))

        file = open(dir+'/for_test/vremena.zip','rb')
        post_form['file'] = file
        response = self.client.post('/cabinet/edit_document/'+str(self.disseminator_document.id)+'/',post_form)
        file.close()

        self.failIf(self.disseminator_document.file.storage.exists(old_file))
        document = Documents.all_objects.get(pk=self.disseminator_document.pk)        

        self.assertNotEqual(old_file,document.file.name)        
        self.failUnless(self.disseminator_document.file.storage.exists(document.file.name))
        document.file.delete()

    def test_saving_not_own_document_with_edit_document_page(self):
        self.login(username='disseminator',password='password')
        post_form = {'title' : 'registration',
                     'description' : 'dgjango-registration document'}
        
        response = self.client.post('/cabinet/edit_document/'+str(self.disseminator2_document.id)+'/',post_form)
        self.assertTemplateUsed(response, 'error.html')

class ActionDeleteDocument(DocumentTestCase):

    def setUp(self):
        super(ActionDeleteDocument,self).setUp()
        from datetime import datetime
        self.disseminator_paid_document = Documents.all_objects.create(path = '/'+str(self.disseminator_section.pk)+'/',
                                                              title='title',description='test document',
                                                              user=self.store_disseminator, file=self.file, 
                                                              file_size=self.file.size, 
                                                              storage = self.store_disseminator_storage,
                                                              cost = "10.40", is_free = False, last_purchase=datetime.now())

        self.PD_deal = Dealings.objects.create(buyer = self.user, seller = self.disseminator,
                                               product = self.disseminator_paid_document,state = 'PD',
                                               cost = self.disseminator_paid_document.cost, date = datetime.now())
    def tearDown(self):
        DocumentTestCase.tearDown(self)
        self.disseminator_paid_document.delete()

    def test_naming_urls(self):
        url = reverse('prospere_delete_document')
        self.assertEqual(url,'/cabinet/delete_document/')

    def test_deleting_own_document_with_disseminator(self):
        self.login(username='disseminator',password='password')
        file = self.disseminator_document.file.name
        storage = self.disseminator.storages_set.get()
        response = self.client.post('/cabinet/delete_document/',{'document_id' : self.disseminator_document.pk})
        self.failIf(self.disseminator_document.file.storage.exists(file))
        count = Documents.all_objects.filter(pk=self.disseminator_document.pk).count()
        self.assertEqual(count,0)
        storage = self.disseminator.storages_set.get()
        self.assertEqual(storage.mem_busy, 0)
        self.assertEqual(response.content,json.dumps({ 'success' : True },sort_keys=True, indent=2))

    def test_deleting_paid_document(self):
        self.login(username='store_disseminator',password='password')
        file = self.disseminator_document.file.name
        response = self.client.post('/cabinet/delete_document/',{'document_id' : self.disseminator_paid_document.pk})
        self.failUnless(self.disseminator_paid_document.file.storage.exists(file))
        count = Documents.all_objects.filter(pk=self.disseminator_paid_document.pk).count()
        self.assertEqual(count,1)
        storage = self.store_disseminator.storages_set.get()
        self.assertEqual(storage.mem_busy, 0)
        self.assertEqual(response.content,json.dumps({ 'success' : True },sort_keys=True, indent=2))

    def test_deleting_not_own_document_with_dissemonator(self):
        self.login(username='disseminator',password='password')
        response = self.client.post('/cabinet/delete_document/',{'document_id' : self.disseminator2_document.pk})
        self.assertEqual(response.content,json.dumps({ 'success' : False, 
                                                       'error' : 'not own document' },sort_keys=True, indent=2))
        
    def test_deleting_with_anonymous(self):
        response = self.client.post('/cabinet/delete_document/',{'document_id' : self.disseminator_document.pk})
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,'/login/?next=/cabinet/delete_document/') 

    def test_getting(self):
        self.login(username='user',password='password')
        response = self.client.get('/cabinet/delete_document/')
        self.assertEqual(response.content,json.dumps({ 'success' : False,'error' : 'wrong method' },sort_keys=True, indent=2))

class ChangeDocumentAccess(DocumentTestCase):

    def test_naming_urls(self):
        url = reverse('prospere_change_document_access')
        self.assertEqual(url,'/cabinet/change_document_access/')

    def test_getting_change_access_document(self):
        self.login(username='disseminator2',password='password')
        response = self.client.get(reverse('prospere_change_document_access'))
        self.assertEqual(response.content,json.dumps({ 'success' : False, 'error' : 'wrong method' },sort_keys=True, indent=2))

    def test_changing_access_without_id(self):
        self.login(username='disseminator2',password='password')
        response = self.client.post(reverse('prospere_change_document_access'))
        self.assertEqual(response.content,json.dumps({ 'success' : False, 'error' : 'missing id' },sort_keys=True, indent=2))

    def test_changing_access_anonymously(self):
        response = self.client.post(reverse('prospere_change_document_access'),{ 'id' : self.disseminator_document.id})
        self.assertRedirects(response,'/login/?next='+reverse('prospere_change_document_access'))

    def test_changing_access_not_own(self):
        self.login(username='disseminator2',password='password')
        response = self.client.post(reverse('prospere_change_document_access'),{ 'id' : self.disseminator_document.id})
        self.assertEqual(response.content,json.dumps({ 'success' : False, 
                                                       'error' : 'permission denied' },sort_keys=True, indent=2))        
    #------------------------------------------
    def test_sharing_access_where_owner_not_shared(self):
        self.disseminator_section.hide()
        self.disseminator_document.hide()
        self.login(username='disseminator',password='password')
        response = self.client.post(reverse('prospere_change_document_access'),{ 'id' : self.disseminator_document.id})
        self.assertEqual(response.content,json.dumps({ 'success' : False, 'error' : 'owner not shared' }, 
                                                       sort_keys = True, indent=2))
        document = Documents.objects.get(id = self.disseminator_document.id)
        self.assertEqual(document.is_shared, False)

    def test_sharing_access_where_owner_shared(self):
        self.disseminator_section.share()
        self.disseminator_document.hide()
        self.login(username='disseminator',password='password')
        response = self.client.post(reverse('prospere_change_document_access'),{ 'id' : self.disseminator_document.id})
        self.assertEqual(response.content,json.dumps({ 'success' : True }, sort_keys = True, indent=2))
        document = Documents.objects.get(id = self.disseminator_document.id)
        self.assertEqual(document.is_shared, True)
    #---------------------
    def test_hiding_access_document(self):
        self.disseminator_document.share()
        self.login(username='disseminator',password='password')
        response = self.client.post(reverse('prospere_change_document_access'),{ 'id' : self.disseminator_document.id })
        self.assertEqual(response.content, json.dumps({ 'success' : True }, sort_keys = True, indent=2))
        document = Documents.objects.get(id = self.disseminator_document.id)
        self.assertEqual(document.is_shared, False)

import re
from django.core.files import File
class CalculateFileHash(DocumentTestCase):

    def test_addition_hash_when_document_create(self):
        dir = os.path.dirname(__file__)
        file = open(dir+'/for_test/file2','rb')
        file = File(file)
        document = Documents.objects.create(path = '/'+str(self.disseminator2_section.pk)+'/',
                                            title='title2', description='test document2', 
                                            user=self.disseminator2, file=file,file_size=file.size, 
                                            storage = self.disseminator2_storage)
        p = re.compile('_[0-9abcdef]{6,6}')
        self.failIf(p.search(document.file.name) is None)
        
        document.delete()

    def test_addition_hash_when_hide_document(self):
        self.disseminator_document.hide()
        p = re.compile('_[0-9abcdef]{6,6}')
        self.failIf(p.search(self.disseminator_document.file.name) is None)

    def test_deleting_hash_when_share_document(self):
        self.disseminator_document.hide()
        document = Documents.objects.get(id = self.disseminator_document.id)
        document.share()
        document = Documents.objects.get(id = self.disseminator_document.id)
        p = re.compile('_[0-9abcdef]{6,6}')
        self.failIf(not p.search(document.file.name) is None)

