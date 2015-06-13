from prospere.contrib.cabinet.models import Documents, Sections, Storages
from prospere.contrib.comment.models import Comments
from prospere.contrib.account.models import Bookmarks
from models import Notifications
from django.contrib.contenttypes.models import ContentType
from operator import attrgetter
from django.contrib.auth.models import User
from django.test import TestCase
from django.core.urlresolvers import reverse
from signal_handlers import *
from django.core.files.base import ContentFile
import json

class NotifTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('user','user@email.ru','password')
        self.user2 = User.objects.create_user('user2','user2@email.ru','password')
        self.user3 = User.objects.create_user('user3','user3@email.ru','password')
        
        self.user_storage = self.user.storages_set.get()
        self.user2_storage = self.user2.storages_set.get()

        self.section = Sections.objects.create(storage=self.user_storage, caption="section", is_shared = True)
        self.user2_section = Sections.objects.create(storage=self.user2_storage, caption="section", is_shared = True)

        self.user_document = Documents.objects.create(path = '/'+str(self.section.pk)+'/',
                                                              title = 'title', description='test document',
                                                              user = self.user, 
                                                              file = ContentFile("my string content"), file_size = 0, 
                                                              storage = self.user_storage, is_shared = False)
        self.user2_document = Documents.objects.create(path = '/'+str(self.user2_section.pk)+'/',
                                                              title = 'title', description='test document',
                                                              user = self.user2, 
                                                              file = ContentFile("my string content"), file_size = 0, 
                                                              storage = self.user2_storage, is_shared = False)
        self.user_top_comment_on_user = Comments.objects.create(comment = "sdf", content_type = 
                                              ContentType.objects.get_for_model(self.user),
                                              object_pk = self.user.id, user = self.user )
        self.user_top_comment_on_user2 = Comments.objects.create(comment = "sdf", content_type = 
                                              ContentType.objects.get_for_model(self.user2),
                                              object_pk = self.user2.id, user = self.user )
        self.user2_top_comment_on_user2 = Comments.objects.create(comment = "sdf", content_type = 
                                              ContentType.objects.get_for_model(self.user2),
                                              object_pk = self.user2.id, user = self.user2 )
        self.user2_top_comment_on_user = Comments.objects.create(comment = "sdf", content_type = 
                                              ContentType.objects.get_for_model(self.user),
                                              object_pk = self.user.id, user = self.user2 )

        Bookmarks.objects.create(user = self.user, type = "UR", object = self.user2.id)
        Bookmarks.objects.create(user = self.user2, type = "UR", object = self.user.id)
        Bookmarks.objects.create(user = self.user3, type = "UR", object = self.user.id)
        Bookmarks.objects.create(user = self.user3, type = "UR", object = self.user2.id)

        Notifications.objects.all().delete()

    def tearDown(self):
        Notifications.objects.all().delete()

class SignallHandlerTest(NotifTestCase):

    '''
    user - owner of new comments
    '''
    def test_addition_nested_comment_on_user_comment_on_user2_page(self):
        c = Comments.objects.create(comment = "sdf", content_type = 
                                ContentType.objects.get_for_model(self.user2),
                                object_pk = self.user2.id, user = self.user, parent = self.user_top_comment_on_user2 )
        count = Notifications.objects.all().count()
        self.assertEquals(count, 1)
        notifications = Notifications.objects.all()
        self.assertQuerysetEqual(notifications, [("AC", self.user.username, self.user2.id, c, )],
                         attrgetter("action", "username", "user_id", "content_object"))

    def test_addition_nested_comment_on_user2_comment_on_user2_page(self):
        c = Comments.objects.create(comment = "sdf", content_type = 
                                ContentType.objects.get_for_model(self.user2),
                                object_pk = self.user2.id, user = self.user, parent = self.user2_top_comment_on_user2 )
        count = Notifications.objects.all().count()
        self.assertEquals(count, 1)
        notifications = Notifications.objects.all()
        self.assertQuerysetEqual(notifications, [("AC", self.user.username, self.user2.id, c, )],
                         attrgetter("action", "username", "user_id", "content_object"))

    def test_addition_nested_comment_on_user2_comment_on_user_page(self):
        c = Comments.objects.create(comment = "sdf", content_type = 
                                ContentType.objects.get_for_model(self.user),
                                object_pk = self.user.id, user = self.user, parent = self.user2_top_comment_on_user )
        count = Notifications.objects.all().count()
        self.assertEquals(count, 1)
        notifications = Notifications.objects.all()
        self.assertQuerysetEqual(notifications, [("AC", self.user.username, self.user2.id, c, )],
                         attrgetter("action", "username", "user_id", "content_object"))

    def test_addition_nested_comment_on_user_comment_on_user_page(self):
        c = Comments.objects.create(comment = "sdf", content_type = 
                                ContentType.objects.get_for_model(self.user),
                                object_pk = self.user.id, user = self.user, parent = self.user_top_comment_on_user )
        count = Notifications.objects.all().count()
        self.assertEquals(count, 0)

    def test_addition_top_comment_on_user2_document_page(self):
        c = Comments.objects.create(comment = "sdf", content_type = 
                                ContentType.objects.get_for_model(self.user2_document),
                                object_pk = self.user2_document.id, user = self.user )
        count = Notifications.objects.all().count()
        self.assertEquals(count, 1)
        notifications = Notifications.objects.all()
        self.assertQuerysetEqual(notifications, [("AC", self.user.username, self.user2.id, c, )],
                         attrgetter("action", "username", "user_id", "content_object"))

    def test_addition_top_comment_to_user(self):
        Comments.objects.create(comment = "sdf", content_type = 
                                ContentType.objects.get_for_model(self.user),
                                object_pk = self.user.id, user = self.user )
        count = Notifications.objects.all().count()
        self.assertEquals(count, 0)        

    def test_addition_top_comment_to_user_document(self):
        Comments.objects.create(comment = "sdf", content_type = 
                                ContentType.objects.get_for_model(self.user_document),
                                object_pk = self.user_document.id, user = self.user )
        count = Notifications.objects.all().count()
        self.assertEquals(count, 0)

    def test_deleting_notifications_when_deleted_comment(self):
        c = Comments.objects.create(comment = "sdf", content_type = 
                                ContentType.objects.get_for_model(self.user2),
                                object_pk = self.user2.id, user = self.user )
        c2 = Comments.objects.create(comment = "sdf", content_type = 
                                ContentType.objects.get_for_model(self.user),
                                object_pk = self.user.id, user = self.user2 )
        count = Notifications.objects.all().count()
        self.assertEquals(count, 2)
        c.delete()
        c2.delete()
        count = Notifications.objects.all().count()
        self.assertEquals(count, 0)

    '''
    Document handlers
    '''
    def test_addition_notif_when_share_document(self):
        self.user_document.share()
        count = Notifications.objects.all().count()
        self.assertEquals(count, 2)
        notifications = Notifications.objects.all()
        self.assertQuerysetEqual(notifications, [("AD", self.user.username, self.user2.id, self.user_document, ),
                                                 ("AD", self.user.username, self.user3.id, self.user_document, )],
                         attrgetter("action", "username", "user_id", "content_object"))

    def test_deleting_notif_when_hide_document(self):
        self.user_document.share()
        self.user_document.hide()
        count = Notifications.objects.all().count()
        self.assertEquals(count, 0)

    def test_addition_notif_when_create_document(self):
        Documents.objects.create(path = '/'+str(self.section.pk)+'/',
                                  title = 'title', description='test document',
                                  user = self.user, 
                                  file = ContentFile("my string content"), file_size = 0, 
                                  storage = self.user_storage, is_shared = False)
        count = Notifications.objects.all().count()
        self.assertEquals(count, 0)

    def test_deleting_notif_when_delete_share_document(self):
        self.user_document.share()
        self.user_document.delete()
        count = Notifications.objects.all().count()
        self.assertEquals(count, 0)

class DeleteNotificationTest(NotifTestCase):

    def test_naming_delete(self):
        url = reverse('prospere_delete_notification')
        self.assertEqual(url,'/notification/delete/')    
    
    def test_deleting_with_anonymous(self):
        response = self.client.post(reverse('prospere_delete_notification'), {})
        self.assertEqual(response.content,json.dumps({ 'success' : False,
                                                       'error' : 'user not authentificated' },sort_keys=True, indent=2))

    def test_getting_delete_notif(self):
        response = self.client.get(reverse('prospere_delete_notification'), {})
        self.assertEqual(response.content,json.dumps({ 'success' : False,
                                                       'error' : 'wrong method' },sort_keys=True, indent=2))

    def test_deleting_missing_id(self):
        self.client.login(username = 'user', password = "password")
        response = self.client.post(reverse('prospere_delete_notification'), {})
        self.assertEqual(response.content,json.dumps({ 'success' : False,
                                                       'error' : 'missing id' },sort_keys=True, indent=2))

    def test_deleting_not_own(self):
        n = Notifications.objects.create(action = "AC", user = self.user2, username="asd", 
                                        content_type = ContentType.objects.get_for_model(self.user),
                                        object_pk = self.user.id)
        self.client.login(username = 'user', password = "password")
        response = self.client.post(reverse('prospere_delete_notification'), { 'id' : n.id})
        self.assertEqual(response.content,json.dumps({ 'success' : False,
                                                       'error' : 'not own' },sort_keys=True, indent=2))
        count = Notifications.objects.all().count()
        self.assertEquals(count, 1)

    def test_deleting_notification(self):
        n = Notifications.objects.create(action = "AC", user = self.user, username="asd", 
                                        content_type = ContentType.objects.get_for_model(self.user),
                                        object_pk = self.user.id)
        self.client.login(username = 'user', password = "password")
        response = self.client.post(reverse('prospere_delete_notification'), { 'id' : n.id})
        self.assertEqual(response.content,json.dumps({ 'success' : True },sort_keys=True, indent=2))
        count = Notifications.objects.all().count()
        self.assertEquals(count, 0)

class BaseNotificationTest(NotifTestCase):

    def test_naming_get_url(self):
        url = reverse('prospere_get_notifications')
        self.assertEqual(url,'/notification/get_notifications/')

    def test_getting_notifs_anonymously(self):
        response = self.client.get(reverse('prospere_get_notifications'))
        self.assertEqual(response.content,json.dumps({ 'success' : False,
                                                       'error' : 'user not authentificated' },sort_keys=True, indent=2))

    def test_getting_document_notif(self):
        self.user2_document.share()
        self.client.login(username = 'user', password = "password")
        response = self.client.get(reverse('prospere_get_notifications'))
        self.failUnless(response.content.count('"action_type": "AD"'))
        self.failUnless(response.content.count('"link": '))
        self.failUnless(response.content.count('"username": "' + self.user2.username + '"'))
        self.failUnless(response.content.count('"text": "' + self.user2_document.title + '"'))
        #self.assertEqual(response.content, "")
        self.failUnless(response.content.count('"success": true'))


    def test_getting_comment_on_user_notif(self):
        n = Notifications.objects.create(action = "AC", user = self.user, username="asd", 
                                        content_type = ContentType.objects.get_for_model(self.user_top_comment_on_user),
                                        object_pk = self.user_top_comment_on_user.id)
        self.client.login(username = 'user', password = "password")
        response = self.client.get(reverse('prospere_get_notifications'))
        self.failUnless(response.content.count('"action_type": "AC"'))
        self.failUnless(response.content.count('"link": '))
        self.failUnless(response.content.count('"username": "' + n.username + '"'))
        self.failUnless(response.content.count('"text": "' + self.user_top_comment_on_user.comment + '"'))
        self.failUnless(response.content.count('"success": true'))

    def test_getting_comment_on_document_notif(self):
        c = Comments.objects.create(comment = "sdf", content_type = 
                                ContentType.objects.get_for_model(self.user2_document),
                                object_pk = self.user2_document.id, user = self.user )
        self.client.login(username = 'user2', password = "password")
        response = self.client.get(reverse('prospere_get_notifications'))
        self.failUnless(response.content.count('"action_type": "AC"'))
        self.failUnless(response.content.count('"link": '))
        self.failUnless(response.content.count('"username": "' + c.user.username + '"'))
        self.failUnless(response.content.count('"text": "' + c.comment + '"'))
        self.failUnless(response.content.count('"success": true'))


