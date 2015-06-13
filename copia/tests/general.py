from prospere.contrib.comment.forms import CommentForm, BondCommentForm
from django.test import TestCase
from prospere.lib.test import ExtraTestCase, DocumentTestCase
from django.contrib.auth.models import User
from prospere.contrib.cabinet.models import Storages, Documents
from prospere.copia.models import SessionBonds
from django.contrib.sessions.models import Session
from operator import attrgetter
from django.core.urlresolvers import reverse
from prospere.contrib.account.models import Bookmarks

class MainTestCase(DocumentTestCase):

    def test_naming_urls(self):
        url = reverse('prospere_search')
        self.assertEqual(url,'/search/')

    def test_getting_start_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'general/start.html')

    def test_getting_start_page_with_login_user(self):
        self.login(username='disseminator',password='password')
        response = self.client.get('/')
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,reverse("prospere_user_page",kwargs={'username':'disseminator'}))

    def test_getting_search_result_page_empty_query(self):
        response = self.client.get(reverse('prospere_search'))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'general/search_results.html')

    def test_getting_search_users(self):
        response = self.client.get(reverse('prospere_search') + '?query=sem')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'general/search_results.html')
        self.assertEqual(response.context['search_query'],'sem')
        self.assertEqual(response.context['documents'], [])
        self.assertEqual(response.context['users'][0].username, 'disseminator')

    def test_getting_search_documents(self):
        response = self.client.get(reverse('prospere_search') + '?query=est')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'general/search_results.html')
        self.assertEqual(response.context['search_query'],'est')
        self.assertEqual(response.context['users'], [])
        #self.assertEqual(response.context['documents'][0].title, 'title2')

class PageDocument(DocumentTestCase):

    def setUp(self):
        DocumentTestCase.setUp(self)
        import os
        dir = os.path.dirname(__file__)
        from django.core.files import File
        file = open(dir+'/for_test/vremena.zip','rb')
        file = File(file)
        self.file = file

        self.hidden_document = Documents.objects.create(path = '/'+str(self.disseminator_section.pk)+'/',
                                                              title='title',description='test document',
                                                              user=self.disseminator,file=file,file_size=file.size, 
                                                              storage = self.disseminator_storage)

    def tearDown(self):
        DocumentTestCase.tearDown(self)
        self.hidden_document.delete()

    def test_naming_urls_pd(self):
        url = reverse('prospere_document', kwargs = {'document_id' : self.disseminator_document.id })
        self.assertEqual(url,'/document/' + str(self.disseminator_document.id) + '/')

    def test_getting_document_page_with_anonymous(self):
        from django.conf import settings
        settings.ALLOW_GET_DOCUMENT_FILES = True
        response = self.client.get(reverse('prospere_document', kwargs = {'document_id' : self.disseminator_document.id}))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'general/document.html') 
        # check fields !!!
        self.failUnless(isinstance(response.context['comment_form'],CommentForm))
        self.assertGetQuerysetEqual(response.context['document'],[( self.disseminator_document.id )],attrgetter("id"))
        self.failUnless(response.context['allow_get_file'])
        self.failUnless(response.context['vote_form'])
        self.failIf(response.context['read_only_vote'])
        self.assertEqual(response.context['user'].id,self.disseminator.id)
        self.assertEqual(response.context['profile'].id,self.disseminator.get_profile().id)

    def test_getting_my_document_page_with_user(self):
        self.login(username='disseminator',password='password')
        response = self.client.get(reverse('prospere_document', kwargs = {'document_id' : self.disseminator_document.id}))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'general/document.html') 
        # check fields !!!
        self.failUnless(response.context['read_only_vote'])
        self.failUnless(isinstance(response.context['comment_form'],BondCommentForm))
        self.assertGetQuerysetEqual(response.context['document'],[( self.disseminator_document.id )],attrgetter("id"))

    def test_getting_document_page_closed_downloading(self):
        self.login(username='disseminator',password='password')
        from django.conf import settings
        settings.ALLOW_GET_DOCUMENT_FILES = False
        response = self.client.get(reverse('prospere_document', kwargs = {'document_id' : self.disseminator_document.id}))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'general/document.html') 
        self.failIf(response.context['allow_get_file'])

    def test_getting_not_exist_document(self):
        response = self.client.get(reverse('prospere_document', kwargs = {'document_id' : 54}))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'error.html') 

    '''
    Getting hidden document
    '''
    def test_getting_my_hidden_document(self):
        self.login(username='disseminator',password='password')
        response = self.client.get(reverse('prospere_document', kwargs = {'document_id' : self.hidden_document.id}))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'general/document.html')

    def test_getting_hidden_document_anonymously(self):
        response = self.client.get(reverse('prospere_document', kwargs = {'document_id' : self.hidden_document.id}))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'error.html') 

    def test_getting_not_my_hidden_document(self):
        response = self.client.get(reverse('prospere_document', kwargs = {'document_id' : self.hidden_document.id}))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'error.html') 

class UserPage(DocumentTestCase):

    def setUp(self):
        DocumentTestCase.setUp(self)
        import os
        dir = os.path.dirname(__file__)
        from django.core.files import File
        file = open(dir+'/for_test/vremena.zip','rb')
        file = File(file)
        self.file = file

        self.hidden_document = Documents.objects.create(path = '/'+str(self.disseminator_section.pk)+'/',
                                                              title='title',description='test document',
                                                              user=self.disseminator,file=file,file_size=file.size, 
                                                              storage = self.disseminator_storage)
    def tearDown(self):
        DocumentTestCase.tearDown(self)
        self.hidden_document.delete()

    def test_naming_urls_up(self):
        url = reverse('prospere_user_page', kwargs = {'username' : self.disseminator.username})
        self.assertEqual(url,'/user/' + self.disseminator.username + '/')

    def test_getting_user_page(self):
        response = self.client.get(reverse("prospere_user_page",kwargs={'username':self.disseminator.username}))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'general/user_page.html')
        self.assertEqual(response.context['user'].id,self.disseminator.id)
        self.assertEqual(response.context['profile'].id,self.disseminator.get_profile().id)
        self.assertEqual(response.context['storage'].user_id,self.disseminator.id)
        self.assertEqual(response.context['add_bookmark'],False)

    def test_getting_my_user_page(self):
        self.login(username='disseminator',password='password')
        response = self.client.get(reverse("prospere_user_page",kwargs={'username':self.disseminator.username}))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'general/user_page.html')
        self.assertEqual(response.context['user'].id,self.disseminator.id)
        self.assertEqual(response.context['profile'].id,self.disseminator.get_profile().id)
        self.assertEqual(response.context['storage'].user_id,self.disseminator.id)
        self.assertEqual(response.context['add_bookmark'],False)

    def test_showing_documents_on_my_page(self):
        self.login(username='disseminator',password='password')
        response = self.client.get(reverse("prospere_user_page",kwargs={'username':self.disseminator.username}))
        self.assertQuerysetEqual(response.context['documents'], [self.hidden_document.id, self.disseminator_document.id],
                                 attrgetter("id"))

    def test_showing_hidden_documents_on_my_page(self):
        self.login(username='disseminator',password='password')
        response = self.client.get(reverse("prospere_user_page",kwargs={'username':self.disseminator.username}))
        self.assertQuerysetEqual(response.context['documents'], [self.hidden_document.id, self.disseminator_document.id],
                                 attrgetter("id"))

    def test_showing_hidden_documents_not_my_page_anonymously(self):
        response = self.client.get(reverse("prospere_user_page",kwargs={'username':self.disseminator.username}))
        self.assertQuerysetEqual(response.context['documents'], [self.disseminator_document.id],
                                 attrgetter("id"))

    def test_showing_hidden_documents_not_my_page(self):
        self.login(username='disseminator2',password='password')
        response = self.client.get(reverse("prospere_user_page",kwargs={'username':self.disseminator.username}))
        self.assertQuerysetEqual(response.context['documents'], [self.disseminator_document.id],
                                 attrgetter("id"))

    def test_getting_user_page_bookmarks_added(self):
        self.login(username='disseminator',password='password')
        response = self.client.post('/account/add_bookmark/',{ 'type' : 'UR', 'object' : self.disseminator2.id })
        response = self.client.get(reverse("prospere_user_page", kwargs={'username':self.disseminator2.username}))
        self.assertEqual(response.context['add_bookmark'],False)

    def test_getting_user_page_bookmarks_not_added(self):
        self.login(username='disseminator',password='password')
        response = self.client.get(reverse("prospere_user_page", kwargs={'username':self.disseminator2.username}))
        self.assertEqual(response.context['add_bookmark'],True)

    def test_getting_profile_page_wrong_user(self):
        response = self.client.get(reverse("prospere_user_page", kwargs={'username' : 'sdf'}))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'error.html')

class LoginTest(ExtraTestCase):

    def setUp(self):
        self.user = User.objects.create_user('user','test@email.ru','password')
        self.bmrk = Bookmarks.objects.create(user = self.user, type = "UR", object = self.user.id)

    def test_login_redirecting(self):
        response = self.client.post(reverse('prospere_login'), {'username':'user',
                                                                'password':'password'})
        self.assertEqual(response.status_code, 302)

    def test_login_few_times(self):
        import time;
        for i in range(1,10+1):
            response = self.client.post(reverse('prospere_login'), {'username':'user',
                                                                    'password':'wrong_password'})

            self.assertEqual(self.client.session['login_count'], i)
            self.failUnless(self.client.session['login_expire_time'] < time.time())

        response = self.client.post(reverse('prospere_login'), {'username':'user',
                                                       'password':'password'})
        self.failIf(self.client.session['login_expire_time'] < time.time()+60*60-1)
        self.failIf(self.client.session['login_expire_time'] > time.time()+60*60+1)
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'error.html') 

class AuthorizationTest(ExtraTestCase):
    '''
    Test login and logout behavior 
    '''
    def test_naming_login_and_logout_url(self):
        url = reverse('prospere_login')
        self.assertEqual(url,'/login/')
        
        url = reverse('prospere_logout')
        self.assertEqual(url,'/logout/')
        
    def setUp(self):
        user = User.objects.create_user('test_user','email','password')
        user.save()

    def test_redirecting_login_page(self):
        response = self.client.post(reverse('prospere_login'),{'username':'test_user',
                                                       'password':'password'})
        self.assertEqual(response.status_code,302)
        
    def test_getting_login_page_with_formerror(self):
        response = self.client.post(reverse('prospere_login'),{'username':'wrong',
                                                       'password':'password'})
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'general/login.html')
        
    def test_getting_login_page(self):
        response = self.client.get(reverse('prospere_login'))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'general/login.html')
        
    def test_redirecting_logout_page(self):
        response = self.client.get(reverse('prospere_logout'))
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,'/')

