"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.core import mail
from django.conf import settings
from django.contrib.auth.models import User

from registration.models import RegistrationProfile
from django.core.urlresolvers import reverse
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.utils.http import int_to_base36
import os
from operator import attrgetter
from django.contrib.auth.forms import PasswordResetForm,SetPasswordForm
from models import UserProfiles, Bookmarks
import json


settings.MEDIA_ROOT = settings.TEST_MEDIA_ROOT

class RegistrationTest(TestCase):
    '''
    Test registration and activation behavior
    ''' 
    def setUp(self):
        '''
        set REGISTRATION_OPEN = true
        '''
        settings.REGISTRATION_OPEN = True
        self.user = User.objects.create_user('exist','test@email.ru','password')
        
    def test_naming_register_urls(self):
        url = reverse('registration_register')
        self.assertEqual(url,'/account/register/')       
        
        url = reverse('registration_activate',kwargs = {'activation_key':'activation_key'})
        self.assertEqual(url,'/account/activate/activation_key/')
               
    def test_redirecting_register_page_to_register_complete_page(self):
        '''
        Email success sended. Than page redirect to 'account/register/complete/'
        '''
        response = self.client.post('/account/register/',{'username':'testuser',
                                                          'email':'kolia@inbox.ru',
                                                          'password1':'qwerty',
                                                          'password2':'qwerty',})
        self.assertRedirects(response,'/?message=account_registration_complete')
        
    '''
    	test_getting_register_page_with_formerror
    '''
    def test_getting_register_page_with_short_username(self):
        '''
        Form contain anyone error. Than page 'account/register/'
        '''
        response = self.client.post('/account/register/',{'username':'as',
                                                          'email':'kolia@inbox.ru',
                                                          'password1':'qwerty',
                                                          'password2':'qwerty',})
        self.assertEqual(response.status_code,200)
        self.failIf(response.context['form'].is_valid())
        self.assertTemplateUsed(response,'registration.html')
        
    def test_getting_register_page_with_short_password(self):
        '''
        Form contain anyone error. Than page 'account/register/'
        '''
        response = self.client.post('/account/register/',{'username':'kolia',
                                                          'email':'kolia@inbox.ru',
                                                          'password1':'qw',
                                                          'password2':'qw',})
        self.assertEqual(response.status_code,200)
        self.failIf(response.context['form'].is_valid())
        self.assertTemplateUsed(response,'registration.html')

    def test_getting_register_page_with_email_that_used(self):
        '''
        Form contain anyone error. Than page 'account/register/'
        '''
        response = self.client.post('/account/register/',{'username':'kolia',
                                                          'email':'test@email.ru',
                                                          'password1':'qwerty',
                                                          'password2':'qwerty',})
        self.assertEqual(response.status_code,200)
        self.failIf(response.context['form'].is_valid())
        self.assertTemplateUsed(response,'registration.html')
        
    def test_redirecting_activate_page_to_activate_complete_page(self):
        """
        Activate code is true. Than page redirect to 'account/activate/complete/'
        """
        response = self.client.post('/account/register/',{ 'username':'user',
                                                          'email':'kolia@inbox.ru',
                                                          'password1':'qwerty',
                                                          'password2':'qwerty',})
        profile = RegistrationProfile.objects.get(user__username='user')                                                 
        response = self.client.get('/account/activate/'+profile.activation_key+'/')
        self.assertRedirects(response,'/?message=account_activate_complete')
        self.failUnless(User.objects.get(username='user').is_active)
        
    def test_getting_activate_page_with_wrong_code(self):
        '''
        Activate code is wrong or doesn't present. Than page 'account/activate/'
        '''
        response = self.client.get('/account/activate/wrong_activate_code/')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'error.html')
        
    def test_getting_register_when_open_false(self):
        '''
        /account/register/closed
        '''
        settings.REGISTRATION_OPEN = False
        response = self.client.get('/account/register/')
        self.assertRedirects(response,'/?message=account_registry_closed')
        self.assertEqual(response.status_code,302)

'''
change by email
'''
class TestForgetPassword(TestCase):

    def setUp(self):
        user = User.objects.create_user('test_user','test@email.ru','password')
        user.save()
        token = token_generator.make_token(user)
        uid = int_to_base36(user.id)
        self.confirm_code = uid + '-' + token
    '''
    Test Behavior Reset page 
        done - email message was sent
    '''
    def test_naming_password_reset_url(self):
        url = reverse('prospere_password_reset')
        self.assertEqual(url,'/account/password/reset/')
    
    def test_getting_reset_password_page(self):    
        response = self.client.get('/account/password/reset/')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'password/reset.html')
        self.failUnless(isinstance(response.context['form'],PasswordResetForm))    
    
    def test_redirecting_password_reset_page_to_reset_done(self):
        response = self.client.post('/account/password/reset/',{'email' : 'test@email.ru'})
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,'/?message=account_email_sended')
        
    def test_getting_reset_failed_page(self):
        response = self.client.post('/account/password/reset/',{'email' : 'wrong@email.as'})
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'password/reset.html')
    '''
    Test behavior new password page
        complete - success change password
    '''
    def test_getting_confirm_page_with_true_code(self):
   
        response = self.client.get('/account/password/reset/confirm/'+self.confirm_code+'/')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'password/reset_confirm.html')
        self.failIf(not response.context['validlink'])
        #self.failIf(not response.context.has_key('form'))
        self.failUnless(isinstance(response.context['form'],SetPasswordForm))
        
    def test_redirecting_confirm_page_to_complete_reset(self):
        response = self.client.post('/account/password/reset/confirm/'+self.confirm_code+'/',{'new_password1':'kolia',
                                                                                              'new_password2':'kolia'})
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,'/?message=account_password_changed')
        
    def test_getting_confirm_page_with_formerror(self):
        response = self.client.post('/account/password/reset/confirm/'+self.confirm_code+'/',{'new_password1':'k',
                                                                                              'new_password2':'kolia'})
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'password/reset_confirm.html')
        self.failIf(not response.context['validlink'])
        self.failUnless(isinstance(response.context['form'],SetPasswordForm))         
        
    def test_getting_confirm_page_with_wrong_code(self):
        response = self.client.get('/account/password/reset/confirm/bad-code/',follow= True)
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'password/reset_confirm.html')            
        self.failIf(response.context['validlink'])        
        
    def test_getting_confirm_page_with_wrong_code(self):
        response = self.client.post('/account/password/reset/confirm/bad-code/',{'new_password1':'kolia',
                                                                                 'new_password2':'kolia'})
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'password/reset_confirm.html')            
        self.failIf(response.context['validlink']) 

'''
 change across profile
'''
class TestChangePassword(TestCase):
    def setUp(self):
        user = User.objects.create_user('test_user','test@email.ru','password')
        self.client.login(username='test_user',password = 'password')
        self.user = user

    def test_naming_password_reset_url(self):
        url = reverse('prospere_password_change')
        self.assertEqual(url,'/account/password/change/')
    
    def test_getting_change_password_page(self):
        response = self.client.get('/account/password/change/')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'password/change.html')

    def test_redirecting_confirm_page_to_complete_reset(self):
        response = self.client.post('/account/password/change/',{ 'old_password' :'password',
                                                                  'new_password1':'kolia',
                                                                  'new_password2':'kolia'})
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,'/profile/?message=account_password_changed')  
 
class SaveProfile(TestCase):
    
    def setUp(self):
        user = User.objects.create_user('test_user','test@email.ru','password')
        self.client.login(username='test_user',password = 'password')
        self.client.user = user
        
    def tearDown(self):
        profile = self.client.user.get_profile()
        profile.delete_picture()
        profile.delete_small_picture()
    
    def test_naming_profile_url(self):
        url = reverse('prospere_save_profile')
        self.assertEqual(url,'/account/save_profile/')
        
        
    def test_getting_profile_page(self):
        response = self.client.get(reverse('prospere_save_profile'))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'error.html')

    def test_getting_page_with_anonymous(self):
        self.client.logout()
        response = self.client.post(reverse('prospere_save_profile'),{})
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,'/login/')
        
    '''
    Testing upload images, deleting, saving
    '''
    
    def test_saving_upload_image(self):
    	dir = os.path.dirname(__file__)
        picture = open(dir+'/for_test/image.jpg',"rb")
        response = self.client.post(reverse('prospere_save_profile'),{ 'picture' : picture, 
                'next' : reverse("prospere_user_page", kwargs={ 'username' : self.client.user.username }) })
        picture.close()
        profile = self.client.user.get_profile()
        self.failUnless(profile.picture.storage.exists(profile.picture.name))
        self.assertNotEqual(profile.picture.name, '')
        self.failUnless(profile.small_picture.storage.exists(profile.small_picture.name))
        self.assertNotEqual(profile.small_picture.name,'')
        self.assertRedirects(response,'/user/test_user/?message=account_profile_saved')
        
    def test_getting_default_pictures(self):
        profile = self.client.user.get_profile()
        url = profile.get_picture_url()
        self.assertEqual(url,settings.MEDIA_URL+'picture/unknown.jpg')
        
        url = profile.get_small_picture_url()
        self.assertEqual(url,settings.MEDIA_URL+'picture/unknown_small.jpg')
        
    def test_deleting_old_pictures(self):
        from django.core.files.storage import default_storage
        
        dir = os.path.dirname(__file__)
        picture = open(dir+'/for_test/image.jpg',"rb")
        response = self.client.post(reverse('prospere_save_profile'),{ 'picture' : picture })
        picture.close()
        
        profile = UserProfiles.objects.get(user = self.client.user)
        
        old_picture_name = profile.picture.name
        old_small_picture_name = profile.small_picture.name
        
        picture = open(dir+'/for_test/image.jpg',"rb")
        response = self.client.post(reverse('prospere_save_profile'),{ 'picture' : picture })
        picture.close()
        
        self.failIf(default_storage.exists(old_picture_name))
        self.failIf(default_storage.exists(old_small_picture_name))
        
        profile = UserProfiles.objects.get(user = self.client.user)
        self.failUnless(default_storage.exists(profile.picture.name))
        self.failUnless(default_storage.exists(profile.small_picture.name))
        
    def test_deleting_unexisting_pictures(self):
        dir = os.path.dirname(__file__)
        picture = open(dir+'/for_test/image.jpg',"rb")
        response = self.client.post(reverse('prospere_save_profile'),{ 'picture' : picture })
        picture.close()
        
        profile = UserProfiles.objects.get(user = self.client.user)
        profile.picture.delete()
        profile.small_picture.delete()
        
        picture = open(dir+'/for_test/image.jpg',"rb")
        response = self.client.post(reverse('prospere_save_profile'), { 'picture' : picture })
        picture.close()
        
    def test_getting_pictures_url_unexisting_pictures(self):
        dir = os.path.dirname(__file__)
        picture = open(dir+'/for_test/image.jpg',"rb")
        response = self.client.post(reverse('prospere_save_profile'), { 'picture' : picture })
        picture.close()
        
        profile = self.client.user.get_profile()
        profile.picture.delete()
        profile.small_picture.delete()
        
        url = profile.get_picture_url()
        self.assertEqual(url,settings.MEDIA_URL+'picture/unknown.jpg')
        
        url = profile.get_small_picture_url()
        self.assertEqual(url,settings.MEDIA_URL+'picture/unknown_small.jpg')
        
    '''
    Testing saving last_name, first_name, description
    '''
    
    def test_saving_first_name(self):
        response = self.client.post(reverse('prospere_save_profile'),{ 'first_name':'first name',
            'next' : reverse("prospere_user_page", kwargs={ 'username' : self.client.user.username }) })
        user = User.objects.get(pk = self.client.user.pk)
        self.assertEqual(user.first_name,'first name')
        self.assertRedirects(response,'/user/test_user/?message=account_profile_saved')
        
    def test_saving_last_name(self):
        response = self.client.post(reverse('prospere_save_profile'),{ 'last_name':'last name',
            'next' : reverse("prospere_user_page", kwargs={ 'username' : self.client.user.username }) })
        user = User.objects.get(pk = self.client.user.pk)
        self.assertEqual(user.last_name,'last name')
        self.assertRedirects(response,'/user/test_user/?message=account_profile_saved')

    def test_saving_description(self):
        response = self.client.post(reverse('prospere_save_profile'),{ 'description':'about me',
            'next' : reverse("prospere_user_page", kwargs={ 'username' : self.client.user.username }) })
        user = User.objects.get(pk = self.client.user.pk)
        self.assertEqual(user.get_profile().description,'about me')
        self.assertRedirects(response,'/user/test_user/?message=account_profile_saved')

class AddBookmark(TestCase):
    def login(self,username,password):
        response = self.client.post('/login/',{'username':username,
                                                       'password':password})
    def setUp(self):
        user = User.objects.create_user('test_user','test@email.ru','password')
        self.user2 = User.objects.create_user('test2_user','test2@email.ru','password')
        self.client.user = user

    def test_naming_password_reset_url(self):
        url = reverse('prospere_add_bookmark')
        self.assertEqual(url,'/account/add_bookmark/')

    def test_addition_bookmark_with_anonymous(self):
        self.client.logout()
        response = self.client.post('/account/add_bookmark/',{ 'type' : 'UR', 'object' : self.user2.id })
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,'/login/')

    def test_addition_bookmark(self):
        self.login(username='test_user',password = 'password')
        response = self.client.post('/account/add_bookmark/',{ 'type' : 'UR', 'object' : self.user2.id })
        self.assertEqual(response.content,json.dumps({ 'success' : True },sort_keys=True, indent=2))
        bmrk = Bookmarks.objects.get(user = self.client.user)
        self.assertQuerysetEqual([bmrk],[("UR", self.user2.id)], attrgetter("type", "object"))

    def test_addition_bookmark_wrong_type(self):
        self.login(username='test_user',password = 'password')
        response = self.client.post('/account/add_bookmark/',{ 'type' : 'DT', 'object' : self.user2.id })
        self.assertEqual(response.content,json.dumps({ 'success' : False },sort_keys=True, indent=2))
        count = Bookmarks.objects.filter(user = self.client.user).count()
        self.assertEqual(count,0)

    def test_addition_bookmark_get_method(self):
        self.login(username='test_user',password = 'password')
        response = self.client.get('/account/add_bookmark/',{ 'type' : 'UR', 'object' : self.user2.id })
        self.assertEqual(response.content,json.dumps({ 'success' : False },sort_keys=True, indent=2))
        count = Bookmarks.objects.filter(user = self.client.user).count()
        self.assertEqual(count,0)

    def test_addition_bookmark_without_object(self):
        self.login(username='test_user',password = 'password')
        response = self.client.get('/account/add_bookmark/',{ 'type' : 'UR' })
        self.assertEqual(response.content,json.dumps({ 'success' : False },sort_keys=True, indent=2))
        count = Bookmarks.objects.filter(user = self.client.user).count()
        self.assertEqual(count,0)

    def test_addition_bookmark_without_type(self):
        self.login(username='test_user',password = 'password')
        response = self.client.get('/account/add_bookmark/',{ 'type' : 'UR', 'object' : self.user2.id })
        self.assertEqual(response.content,json.dumps({ 'success' : False },sort_keys=True, indent=2))
        count = Bookmarks.objects.filter(user = self.client.user).count()
        self.assertEqual(count,0)

class DeleteBookmark(TestCase):
    def login(self,username,password):
        response = self.client.post('/login/',{'username':username,
                                                       'password':password})
    def setUp(self):
        user = User.objects.create_user('test_user','test@email.ru','password')
        self.user2 = User.objects.create_user('test2_user','test2@email.ru','password')
        self.client.user = user
        self.bmrk = Bookmarks.objects.create(user = user, type = "UR", object = self.user2.id)

    def test_naming_password_reset_url(self):
        url = reverse('prospere_delete_bookmark')
        self.assertEqual(url,'/account/delete_bookmark/')

    def test_deleting_bookmark_with_anonymous(self):
        self.client.logout()
        response = self.client.post('/account/delete_bookmark/',{ 'type' : 'UR', 'object' : self.user2.id })
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,'/login/')

    def test_deleting_bookmark(self):
        self.login(username='test_user',password = 'password')
        response = self.client.post('/account/delete_bookmark/',{ 'type' : 'UR', 'object' : self.user2.id })
        self.assertEqual(response.content,json.dumps({ 'success' : True },sort_keys=True, indent=2))
        count = Bookmarks.objects.filter(user = self.client.user).count()
        self.assertEqual(count,0)

    def test_deleting_not_exist_bookmark(self):
        self.login(username='test_user',password = 'password')
        response = self.client.post('/account/delete_bookmark/',{ 'type' : 'UR', 'object' : 5 })
        self.assertEqual(response.content,json.dumps({ 'success' : False },sort_keys=True, indent=2))

    def test_deleting_bookmark_get_method(self):
        self.login(username='test_user',password = 'password')
        response = self.client.get('/account/add_bookmark/',{ 'type' : 'UR', 'object' : self.user2.id })
        self.assertEqual(response.content,json.dumps({ 'success' : False },sort_keys=True, indent=2))
        count = Bookmarks.objects.filter(user = self.client.user).count()
        self.assertEqual(count,1)

from . import vote_user
from decimal import Decimal
class UserVote(TestCase):

    def setUp(self):
        user = User.objects.create_user('test_user','test@email.ru','password')
        self.user = user

    def test_vote(self):
        profile = UserProfiles.objects.get(user=self.user.id)
    	self.assertEqual(profile.count_vote, 0)
    	self.assertEqual(profile.mark, 0)
    	
        vote_user(self.user, str(4.5))
        profile = UserProfiles.objects.get(user=self.user.id)
        self.assertEqual(profile.count_vote, 1)
        self.assertEqual(profile.mark, Decimal(str(4.5)))

        vote_user(self.user.id, 3)
        profile = UserProfiles.objects.get(user=self.user.id)        
        self.assertEqual(profile.count_vote, 2)
        self.assertEqual(profile.mark, Decimal(str(3.8)))

class CheckUsername(TestCase):

    def setUp(self):
        user = User.objects.create_user('test_user','test@email.ru','password')
        self.user = user

    def test_check_username_url(self):
        url = reverse('prospere_check_username')
        self.assertEqual(url,'/account/check_username/')

    def test_checking_already_exist_username(self):
        response = self.client.get(reverse("prospere_check_username"), { 'username' : self.user.username })
        self.assertEqual(response.content,json.dumps({ 'success' : True, 'username_free' : False },sort_keys=True, indent=2))

    def test_checking_not_exist_username(self):
        response = self.client.get(reverse("prospere_check_username"), { 'username' : 'new_username' })
        self.assertEqual(response.content,json.dumps({ 'success' : True, 'username_free' : True },sort_keys=True, indent=2))

    def test_checking_without_username(self):
        response = self.client.get(reverse("prospere_check_username"),)
        self.assertEqual(response.content,json.dumps({ 'success' : False },sort_keys=True, indent=2))


class GetBookmarks(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('test_user','test@email.ru','password')
        self.user2 = User.objects.create_user('test_user2','test2@email.ru','password')

    def test_naming(self):
        url = reverse('prospere_get_bookmarks')
        self.assertEqual(url,'/account/get_bookmarks/')

    def test_get(self):
        Bookmarks.objects.create(user = self.user, type = "UR", object = self.user.id)
        Bookmarks.objects.create(user = self.user, type = "UR", object = self.user2.id)
        response = self.client.get(reverse('prospere_get_bookmarks'), { "id" : self.user.id })
        self.failUnless(response.content.count('"name": "test_user"'))
        self.failUnless(response.content.count('"name": "test_user2"'))

    def test_getting_without_id(self):
        response = self.client.get(reverse('prospere_get_bookmarks'))
        self.assertEqual(response.content,'{\n  "error": "id missed", \n  "success": false\n}')

