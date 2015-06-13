from prospere.lib.test import ExtraTestCase, DocumentTestCase
from prospere.contrib.cabinet.forms import AddDocumentForm, EditDocumentForm, AddSectionForm
from prospere.contrib.cabinet.models import Documents, Sections
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
import os
from django.core.files import File
from django.db.models import Q
from django.conf import settings
import json
from operator import attrgetter

class ActionAddSection(DocumentTestCase):
    def test_naming_urls(self):
        url = reverse('prospere_add_section')
        self.assertEqual(url,'/cabinet/add_section/')
    '''
    disseminator user
    '''
    def test_adding_top_section(self):
        self.login(username='disseminator',password='password')
        response = self.client.post('/cabinet/add_section/',{ 'section_caption':'section',
                                                              'owner_section' : '',
                                                              'storage' : self.disseminator_storage.id,})
        section = Sections.objects.get(caption = "section")
        self.assertEqual(response.content,json.dumps({ 'success' : True,'id' : section.id },sort_keys=True, indent=2))
        self.assertEqual(section.storage.pk,self.disseminator_storage.id)
        self.assertEqual(section.is_shared, False)
        self.assertEqual(section.path,'/')

    def test_adding_internal_sections(self):
        self.login(username='disseminator',password='password')
        response = self.client.post('/cabinet/add_section/',{ 'section_caption':'section',
                                                              'owner_section':str(self.section1_0.pk),
                                                              'storage' : self.disseminator_storage.id,})
        section = Sections.objects.get(caption = "section")
        self.assertEqual(response.content,json.dumps({ 'success' : True,'id' : section.id },sort_keys=True, indent=2))
        self.assertEqual(section.storage.pk,self.disseminator_storage.id)
        self.assertEqual(section.is_shared, False)
        self.assertEqual(section.path,'/'+str(self.section1_0.pk)+'/')
        
    def test_adding_section_wrong_depth(self):
    	settings.MAX_PATH_DEPTH = 4
    	path='/45/45/2334/'
        self.section = Sections.objects.create(storage=self.disseminator_storage, caption="section1_1", path=path)
        self.login(username='disseminator',password='password')
        response = self.client.post('/cabinet/add_section/',{ 'section_caption':'section',
                                                              'owner_section' : str(self.section.id),
                                                              'storage' : self.disseminator_storage.id,})
        self.assertEqual(response.content,json.dumps({ 'success' : False,
                                                       'error' : 'depth is to large' },sort_keys=True, indent=2))
    '''missing'''
    def test_adding_internal_sections_miss_storage_id(self):
        self.login(username='disseminator',password='password')
        response = self.client.post('/cabinet/add_section/',{ 'section_caption':'section',
                                                              'owner_section':str(self.section1_0.pk)})
        self.assertEqual(response.content,json.dumps({ 'success' : False, 
                                                       'error' : 'missing storage_id' },sort_keys=True, indent=2))

    def test_adding_internal_sections_miss_caption(self):
        self.login(username='disseminator',password='password')
        response = self.client.post('/cabinet/add_section/',{ 'storage' : self.disseminator_storage.id,
                                                              'owner_section':str(self.section1_0.pk)})
        self.assertEqual(response.content,json.dumps({ 'success' : False,
                                                       'error' : 'not valid params' },sort_keys=True, indent=2))

    def test_adding_top_section_miss_owner_section(self):
        self.login(username='disseminator',password='password')
        response = self.client.post('/cabinet/add_section/',{ 'section_caption':'section',
                                                              'storage' : self.disseminator_storage.id,})
        section = Sections.objects.get(caption = "section")
        self.assertEqual(response.content,json.dumps({ 'success' : True,'id' : section.id },sort_keys=True, indent=2))
        self.assertEqual(section.storage.pk,self.disseminator_storage.id)
        self.assertEqual(section.is_shared, False)
        self.assertEqual(section.path,'/')
    '''not own'''
    def test_adding_section_to_not_own_section(self):
        self.login(username='disseminator',password='password')
        response = self.client.post('/cabinet/add_section/' ,{ 'section_caption':'section',
                                                               'owner_section':str(self.d2_section1_0.pk),
                                                               'storage' : self.disseminator_storage.id,})
        self.assertEqual(response.content,json.dumps({ 'success' : False, 'error' : 
                                                       'wrong owner section id' },sort_keys=True, indent=2))

    def test_adding_top_section_to_not_own_storage(self):
        self.login(username='disseminator',password='password')
        response = self.client.post('/cabinet/add_section/' ,{ 'section_caption':'section',
                                                               'owner_section':'',
                                                               'storage' : self.disseminator2_storage.id,})
        self.assertEqual(response.content,json.dumps({ 'success' : False, 'error' : 
                                                       'permission denied' },sort_keys=True, indent=2))

    def test_adding_section_to_not_own_storage_and_not_own_section(self):
        self.login(username='disseminator',password='password')
        response = self.client.post('/cabinet/add_section/' ,{ 'section_caption':'section',
                                                               'owner_section':str(self.d2_section1_0.pk),
                                                               'storage' : self.disseminator2_storage.id,})
        self.assertEqual(response.content,json.dumps({ 'success' : False, 'error' : 
                                                       'permission denied' },sort_keys=True, indent=2))

    def test_getting_addition_saction(self):
        self.login(username='disseminator',password='password')
        response = self.client.get('/cabinet/delete_document/')
        self.assertEqual(response.content,json.dumps({ 'success' : False, 
                                                       'error' : 'wrong method' },sort_keys=True, indent=2))

    def test_adding_section_with_anonymous(self):
        response = self.client.post('/cabinet/add_section/' ,{ 'section_caption':'section',
                                                               'owner_section':str(self.d2_section1_0.pk) })
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,'/login/?next=/cabinet/add_section/') 

class ActionEditSection(DocumentTestCase):
    def test_naming_urls(self):
        url = reverse('prospere_edit_section')
        self.assertEqual(url,'/cabinet/edit_section/')

    def test_saving_section(self):
        self.login(username='disseminator',password='password')
        post_form = { 'section_caption':'New books',
                      'section_id' : str(self.disseminator_section.pk) }
        path = self.disseminator_section.path
        response = self.client.post('/cabinet/edit_section/',post_form)
        self.assertEqual(response.content,json.dumps({ 'success' : True },sort_keys=True, indent=2))
        sections = Sections.objects.get(id = self.disseminator_section.pk)
        self.assertEqual(sections.caption,post_form['section_caption'])
        self.assertEqual(sections.path, path)

    def test_saving_not_own_section(self):
        self.login(username='disseminator',password='password')
        post_form = { 'section_caption':'New books',
                      'section_id' : str(self.disseminator2_section.pk) }
        caption = self.disseminator2_section.caption
        response = self.client.post('/cabinet/edit_section/',post_form)
        self.assertEqual(response.content,json.dumps({ 'success' : False, 
                                                      'error' : 'not own section' },sort_keys=True, indent=2))

        sections = Sections.objects.get(id = self.disseminator_section.pk)
        self.assertEqual(sections.caption,caption)

    def test_saving_section_miss_id(self):
        self.login(username='disseminator',password='password')
        post_form = { 'section_caption':'New books'}
        path = self.disseminator_section.path
        response = self.client.post('/cabinet/edit_section/',post_form)
        self.assertEqual(response.content,json.dumps({ 'success' : False, 'error' : 'missing id' },sort_keys=True, indent=2))

    def test_saving_section_miss_caption(self):
        self.login(username='disseminator',password='password')
        post_form = { 'section_id' : str(self.disseminator_section.pk)}
        path = self.disseminator_section.path
        response = self.client.post('/cabinet/edit_section/',post_form)
        self.assertEqual(response.content,json.dumps({ 'success' : False, 
                                                      'error' : 'missing caption'},sort_keys=True, indent=2))

    def test_saving_section_anonymous(self):
        post_form = { 'section_caption':'New books',
                      'section_id' : str(self.disseminator2_section.pk) }
        response = self.client.post('/cabinet/delete_section/',post_form)
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,'/login/?next=/cabinet/delete_section/') 

    def test_getting_edit_page(self):
        self.login(username='disseminator',password='password')
        post_form = { 'section_caption':'New books',
                      'section_id' : str(self.disseminator2_section.pk) }
        response = self.client.get('/cabinet/edit_section/',post_form)
        self.assertEqual(response.content,json.dumps({ 'success' : False,'error' : 'wrong method' },sort_keys=True, indent=2))

class ActionDeleteSection(DocumentTestCase):

    def test_naming_urls(self):
        url = reverse('prospere_delete_section')
        self.assertEqual(url,'/cabinet/delete_section/')

    def test_deleting_section(self):
        self.login(username='disseminator',password='password')
        response = self.client.post('/cabinet/delete_section/', { 'section_id' : self.section1_1.pk })
        self.assertEqual(response.content,json.dumps({ 'success' : True },sort_keys=True, indent=2))
        count = Sections.objects.filter(id = self.section1_1.pk).count()
        self.assertEqual(count, 0)

    def test_deleting_section_not_empty(self):
        self.login(username='disseminator',password='password')
        response = self.client.post('/cabinet/delete_section/', { 'section_id' : self.disseminator_section.pk })
        self.assertEqual(response.content,json.dumps({ 'success' : False, 'error' : 'not empty' },sort_keys=True, indent=2))
        count = Sections.objects.filter(id = self.disseminator_section.pk).count()
        self.assertEqual(count, 1)

    def test_deleting_section_not_own(self):
        self.login(username='disseminator',password='password')
        response = self.client.post('/cabinet/delete_section/', { 'section_id' : self.disseminator2_section.pk })
        self.assertEqual(response.content,json.dumps({ 'success' : False, 'error' : 'not own' },sort_keys=True, indent=2))

    def test_deleting_section_miss_id(self):
        self.login(username='disseminator',password='password')
        response = self.client.post('/cabinet/delete_section/', { })
        self.assertEqual(response.content,json.dumps({ 'success' : False, 'error' : 'missing id' },sort_keys=True, indent=2))

    def test_deleting_section_anonymous(self):
        response = self.client.post('/cabinet/delete_section/',{ 'section_id' : self.disseminator_section.pk })
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,'/login/?next=/cabinet/delete_section/') 

    def test_getting_delete_section(self):
        self.login(username='user',password='password')
        response = self.client.get('/cabinet/delete_section/')
        self.assertEqual(response.content,json.dumps({ 'success' : False, 'error' : 'wrong method' },sort_keys=True, indent=2))

class ChangeSectionAccess(DocumentTestCase):

    def test_naming_urls(self):
        url = reverse('prospere_change_section_access')
        self.assertEqual(url,'/cabinet/change_section_access/')

    def test_getting_change_access_section(self):
        self.login(username='disseminator2',password='password')
        response = self.client.get(reverse('prospere_change_section_access'))
        self.assertEqual(response.content,json.dumps({ 'success' : False, 'error' : 'wrong method' },sort_keys=True, indent=2))

    def test_changing_access_without_id(self):
        self.login(username='disseminator2',password='password')
        response = self.client.post(reverse('prospere_change_section_access'))
        self.assertEqual(response.content,json.dumps({ 'success' : False, 'error' : 'missing id' },sort_keys=True, indent=2))

    def test_changing_access_anonymously(self):
        response = self.client.post(reverse('prospere_change_section_access'),{ 'id' : self.disseminator_section.id})
        self.assertRedirects(response,'/login/?next='+reverse('prospere_change_section_access'))

    def test_changing_access_not_own(self):
        self.login(username='disseminator2',password='password')
        response = self.client.post(reverse('prospere_change_section_access'),{ 'id' : self.disseminator_section.id})
        self.assertEqual(response.content,json.dumps({ 'success' : False, 
                                                       'error' : 'permission denied' },sort_keys=True, indent=2))        
    #------------------------------------------
    def test_sharing_access_where_owner_not_shared(self):
        self.section1_1.hide()
        self.section1_0.hide()
        self.login(username='disseminator',password='password')
        response = self.client.post(reverse('prospere_change_section_access'),{ 'id' : self.section1_1.id})
        self.assertEqual(response.content,json.dumps({ 'success' : False, 'error' : 'owner not shared' }, 
                                                       sort_keys = True, indent=2))
        section = Sections.objects.get(id = self.section1_1.id)
        self.assertEqual(section.is_shared, False)

    def test_sharing_access_top(self):
        self.section1_1.hide()
        self.section1_0.hide()
        self.login(username='disseminator',password='password')
        response = self.client.post(reverse('prospere_change_section_access'),{ 'id' : self.section1_0.id})
        self.assertEqual(response.content,json.dumps({ 'success' : True }, sort_keys = True, indent=2))
        section = Sections.objects.get(id = self.section1_0.id)
        self.assertEqual(section.is_shared, True)
        section = Sections.objects.get(id = self.section1_1.id)
        self.assertEqual(section.is_shared, False)

    def test_sharing_access_internal_section_where_owner_shared(self):
        self.section1_1.hide()
        self.section1_0.share()
        self.login(username='disseminator',password='password')
        response = self.client.post(reverse('prospere_change_section_access'),{ 'id' : self.section1_1.id})
        self.assertEqual(response.content,json.dumps({ 'success' : True }, sort_keys = True, indent=2))
        section = Sections.objects.get(id = self.section1_1.id)
        self.assertEqual(section.is_shared, True)
    #---------------------
    def test_hiding_access_top_section(self):
        self.section1_0.share()
        self.section1_1.share()
        self.section2_1.share()
        self.disseminator_document.path = self.section1_0.path + str(self.section1_0.id) + '/'
        self.disseminator_document.is_shared = True
        self.disseminator_document.save()
        self.login(username='disseminator',password='password')
        response = self.client.post(reverse('prospere_change_section_access'),{ 'id' : self.section1_0.id})
        self.assertEqual(response.content,json.dumps({ 'success' : True }, sort_keys = True, indent=2))
        section = Sections.objects.get(id = self.section1_0.id)
        self.assertEqual(section.is_shared, False)
        section = Sections.objects.get(id = self.section1_1.id)
        self.assertEqual(section.is_shared, False)
        section = Sections.objects.get(id = self.section2_1.id)
        self.assertEqual(section.is_shared, False)
        document = Documents.objects.get(id = self.disseminator_document.id)
        self.assertEqual(document.is_shared, False)

    def test_hiding_access_internal_section(self):
        self.section1_0.share()
        self.section1_1.share()
        self.section2_1.share()
        self.disseminator_document.path = self.section1_1.path + str(self.section1_1.id) + '/'
        self.disseminator_document.is_shared = True
        self.disseminator_document.save()
        self.login(username='disseminator',password='password')
        response = self.client.post(reverse('prospere_change_section_access'),{ 'id' : self.section1_1.id})
        self.assertEqual(response.content,json.dumps({ 'success' : True }, sort_keys = True, indent=2))
        section = Sections.objects.get(id = self.section1_0.id)
        self.assertEqual(section.is_shared, True)
        section = Sections.objects.get(id = self.section1_1.id)
        self.assertEqual(section.is_shared, False)
        section = Sections.objects.get(id = self.section2_1.id)
        self.assertEqual(section.is_shared, True)
        section = Documents.objects.get(id = self.disseminator_document.id)
        self.assertEqual(section.is_shared, False)

    def test_hiding_access_internal_section2(self):
        self.section1_0.share()
        self.section1_1.share()
        self.section2_1.share()
        self.disseminator_document.path = self.section1_1.path
        self.disseminator_document.is_shared = True
        self.disseminator_document.save()
        self.login(username='disseminator',password='password')
        response = self.client.post(reverse('prospere_change_section_access'),{ 'id' : self.section1_1.id})
        self.assertEqual(response.content,json.dumps({ 'success' : True }, sort_keys = True, indent=2))
        section = Sections.objects.get(id = self.section1_0.id)
        self.assertEqual(section.is_shared, True)
        section = Sections.objects.get(id = self.section1_1.id)
        self.assertEqual(section.is_shared, False)
        section = Sections.objects.get(id = self.section2_1.id)
        self.assertEqual(section.is_shared, True)
        section = Documents.objects.get(id = self.disseminator_document.id)
        self.assertEqual(section.is_shared, True)

