from django.test import TestCase
from ..comment import get_comment_form
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from models import Comments
from operator import attrgetter
from django.contrib.contenttypes.models import ContentType
import json

def get_comment_post_data(object,is_user=True):
    from forms import CommentForm,BondCommentForm
    if is_user: form = BondCommentForm(target_object=object)
    else: form = CommentForm(target_object=object)
    post_data={}
    form.hidden = form.get_hidden()
    for name,field in form.fields.items():
        post_data[name] = form.initial.get(name,'')
    post_data['comment'] = "New Comment"
    return post_data;

class PostComment(TestCase):
        
    def setUp(self):
        self.user = User.objects.create_user('user','user@email.ru','password')
        self.object_for_comment = self.user

    def tearDown(self):
        pass
        #settings.test_wrapper.delete()
        
    def test_naming_urls(self):
        url = reverse('prospere_post_comment')
        self.assertEqual(url,'/comments/post_comment/')
        
    def test_posting_object_comment_to_not_exit_object(self):
        self.client.login(username='user',password='password')
        post_data = get_comment_post_data(self.object_for_comment, is_user=True)
        comment_text = "Hello world!"
        post_data['comment'] = comment_text
        post_data['object_pk'] = 1000
        
    	response = self.client.post(reverse('prospere_post_comment'),post_data)
        content_type = ContentType.objects.get_for_model(self.object_for_comment)
        
        value = []
        comment = Comments.objects.filter(user=self.user)
        self.assertQuerysetEqual(comment,value,
                                 attrgetter("content_type","object_pk","user","name","comment",
                                            "is_moderate","is_removed"))
        self.assertTemplateUsed(response,'error.html')

    def test_posting_object_comment_with_user(self):
        self.client.login(username='user',password='password')
        post_data = get_comment_post_data(self.object_for_comment,is_user=True)
        comment_text = "Hello world!"
        post_data['comment'] = comment_text
        
    	response = self.client.post(reverse('prospere_post_comment'),post_data)
        content_type = ContentType.objects.get_for_model(self.object_for_comment)
        
        value = [( content_type,
                   self.object_for_comment.pk,
                   self.user,
                   "",
                   comment_text,
                   False,
                   False,
                   None, )]
        comment = Comments.objects.filter(user=self.user)
        self.assertQuerysetEqual(comment,value,
                                 attrgetter("content_type","object_pk","user","name","comment",
                                            "is_moderate","is_removed","parent"))
        self.assertEqual(response.status_code,302)
        
    def test_posting_object_comment_with_anonymous(self):
        post_data = get_comment_post_data(self.object_for_comment,is_user=False)
        comment_text = "Hello world!"
        post_data['comment'] = comment_text
        post_data['name'] = "name"
        
    	response = self.client.post(reverse('prospere_post_comment'),post_data)
        content_type = ContentType.objects.get_for_model(self.object_for_comment)
        
        value = [( content_type,
                   self.object_for_comment.pk,
                   None,
                   "name",
                   comment_text,
                   False,
                   False,
                   None, )]
        count = Comments.objects.all().count()
        self.assertEqual(count, 0)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,'error.html')
        
    def test_getting_object_comment(self):
        response = self.client.get(reverse('prospere_post_comment'))
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'error.html')
    '''
    Posting wrong security data with user
    '''
    def test_posting_object_comment_with_wrong_timestamp(self):
        self.client.login(username='user',password='password')
        post_data = get_comment_post_data(self.object_for_comment)
        post_data['timestamp'] = int(post_data['timestamp']) + 60*60+1
        response = self.client.post(reverse('prospere_post_comment'),post_data)
        
        count = Comments.objects.all().count()
        self.assertEqual(count,0)
        self.assertTemplateUsed(response,'error.html')   
        
    def test_posting_object_comment_with_not_empty_trick(self):
        self.client.login(username='user',password='password')
        post_data = get_comment_post_data(self.object_for_comment)
        post_data['trick'] = "something"
        response = self.client.post(reverse('prospere_post_comment'),post_data)
        
        count = Comments.objects.all().count()
        self.assertEqual(count,0)
        self.assertTemplateUsed(response,'error.html')   
        
    def test_posting_object_comment_with_wrong_object_pk(self):
        self.client.login(username='user',password='password')
        post_data = get_comment_post_data(self.object_for_comment)
        post_data['object_pk'] = 1
        response = self.client.post(reverse('prospere_post_comment'),post_data)
        
        count = Comments.objects.all().count()
        self.assertEqual(count,0)
        self.assertTemplateUsed(response,'error.html')   
        
    def test_posting_object_comment_with_wrong_content_type(self):
        self.client.login(username='user',password='password')
        post_data = get_comment_post_data(self.object_for_comment)
        post_data['content_type'] = 'auth.ugug'
        response = self.client.post(reverse('prospere_post_comment'),post_data)
        
        count = Comments.objects.all().count()
        self.assertEqual(count,0)
        self.assertTemplateUsed(response,'error.html')   
        
    def test_posting_object_comment_with_wrong_security_hash(self):
        self.client.login(username='user',password='password')
        post_data = get_comment_post_data(self.object_for_comment)
        post_data['security_hash'] = '1376374637137637463713763746371376374637'
        response = self.client.post(reverse('prospere_post_comment'),post_data)
        
        count = Comments.objects.all().count()
        self.assertEqual(count,0)
        self.assertTemplateUsed(response,'error.html')   
        

class CommetnsTree(TestCase):
    '''
    Test building comments tree with different ways : ajax, normal post.
    '''

    def setUp(self):
        self.user = User.objects.create_user('user','user@email.ru','password')
        self.object_for_comment = self.user

    def test_naming_urls(self):
        url = reverse('prospere_post_comment_ajax')
        self.assertEqual(url,'/comments/post_comment_ajax/')

    def test_addition_parent_comment(self):
        self.client.login(username='user',password='password')
        post_data = get_comment_post_data(self.object_for_comment,is_user=True)
        comment_text = "Hello world!"
        post_data['comment'] = comment_text
        
    	response = self.client.post(reverse('prospere_post_comment'),post_data)
        content_type = ContentType.objects.get_for_model(self.object_for_comment)
        value = [( content_type,
                   self.object_for_comment.pk,
                   self.user,
                   "",
                   comment_text,
                   False,
                   False,
                   None, )]
        comment = Comments.objects.filter(user=self.user)
        self.assertQuerysetEqual(comment,value,
                                 attrgetter("content_type","object_pk","user","name","comment",
                                            "is_moderate","is_removed","parent"))
        self.assertEqual(response.status_code,302)
        comment.delete();
        # ajax
    	response = self.client.post(reverse('prospere_post_comment_ajax'),post_data)
        self.assertQuerysetEqual(comment,value,
                                 attrgetter("content_type","object_pk","user","name","comment",
                                            "is_moderate","is_removed","parent"))
        comment = Comments.objects.filter(user=self.user)
        comment.delete();

    def test_addition_nested_comment(self):
        top_comment = Comments.objects.create(comment = "sdf", content_type = 
                                                                   ContentType.objects.get_for_model(self.object_for_comment),
                                              object_pk = self.object_for_comment.id, user = self.user )
        self.client.login(username='user',password='password')
        post_data = get_comment_post_data(self.object_for_comment,is_user=True)
        comment_text = "nested"
        post_data['comment'] = comment_text
        post_data['comment_id'] = top_comment.id
        
    	response = self.client.post(reverse('prospere_post_comment'),post_data)
        content_type = ContentType.objects.get_for_model(self.object_for_comment)
        value = [( content_type,
                   self.object_for_comment.pk,
                   self.user,
                   "",
                   comment_text,
                   False,
                   False,
                   top_comment, )]
        comment = Comments.objects.filter(user=self.user, comment = comment_text)

        self.assertQuerysetEqual(comment,value,
                                 attrgetter("content_type","object_pk","user","name","comment",
                                            "is_moderate","is_removed","parent"))
        self.assertEqual(response.status_code,302)
        comment.delete();
        # ajax
    	response = self.client.post(reverse('prospere_post_comment_ajax'),post_data)
        self.assertQuerysetEqual(comment,value,
                                 attrgetter("content_type","object_pk","user","name","comment",
                                            "is_moderate","is_removed","parent"))
        comment = Comments.objects.filter(user=self.user, comment = comment_text)
        comment.delete();

class EditCommentAjax(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('user','user@email.ru','password')
        self.user2 = User.objects.create_user('user2','user2@email.ru','password')
        self.object_for_comment = self.user
        self.top_comment = Comments.objects.create(comment = "sdf", content_type = 
                                              ContentType.objects.get_for_model(self.object_for_comment),
                                              object_pk = self.object_for_comment.id, user = self.user )

    def test_naming_urls(self):
        url = reverse('prospere_edit_comment_ajax')
        self.assertEqual(url,'/comments/edit_comment_ajax/')

    def test_getting_edit_comment(self):
        response = self.client.get(reverse('prospere_edit_comment_ajax'))
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.content,json.dumps({ 'success' : False, 'error' : 'wrong method' },sort_keys=True, indent=2))

    def test_edition_comment(self):
        self.client.login(username='user',password='password')
        post_data = get_comment_post_data(self.object_for_comment,is_user=True)
        comment_text = "New comment text"
        post_data['comment'] = comment_text
        post_data['comment_id'] = self.top_comment.id
        
    	response = self.client.post(reverse('prospere_edit_comment_ajax'),post_data)
        content_type = ContentType.objects.get_for_model(self.object_for_comment)
        value = [( content_type,
                   self.object_for_comment.pk,
                   self.user,
                   "",
                   comment_text,
                   False,
                   False,
                   None, )]
        comment = Comments.objects.filter(id = self.top_comment.id)
        self.assertQuerysetEqual(comment,value,
                                 attrgetter("content_type","object_pk","user","name","comment",
                                            "is_moderate","is_removed","parent"))
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.content,json.dumps({ 'success' : True },sort_keys=True, indent=2))
        
    '''
    wrong actions
    '''
    def test_edition_comment_with_anonymous(self):
        post_data = get_comment_post_data(self.object_for_comment,is_user=True)
        comment_text = "New comment text"
        post_data['comment'] = comment_text
        post_data['comment_id'] = self.top_comment.id
        
    	response = self.client.post(reverse('prospere_edit_comment_ajax'),post_data)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.content,json.dumps({ 'success' : False, 'error' : 'not authenticated' },
                            sort_keys=True, indent=2))

    def test_edition_comment_permission_denied(self):
        self.client.login(username='user2',password='password')
        post_data = get_comment_post_data(self.object_for_comment,is_user=True)
        comment_text = "New comment text"
        post_data['comment'] = comment_text
        post_data['comment_id'] = self.top_comment.id
        
    	response = self.client.post(reverse('prospere_edit_comment_ajax'),post_data)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.content,json.dumps({ 'success' : False,  'error' : 'permission denied' },
                            sort_keys=True, indent=2))

    def test_edition_comment_nested_comments(self):
        Comments.objects.create(comment = "sdf", content_type = 
                                ContentType.objects.get_for_model(self.object_for_comment),
                                object_pk = self.object_for_comment.id, user = self.user, parent = self.top_comment)
        self.client.login(username='user',password='password')
        post_data = get_comment_post_data(self.object_for_comment,is_user=True)
        comment_text = "New comment text"
        post_data['comment'] = comment_text
        post_data['comment_id'] = self.top_comment.id
        
    	response = self.client.post(reverse('prospere_edit_comment_ajax'),post_data)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.content,json.dumps({ 'success' : False, 'error' : 'has child comments' },
                            sort_keys=True, indent=2))

class DeleteCommentAJAX(TestCase):

    def setUp(self):
        self.user = User.objects.create_user('user','user@email.ru','password')
        self.user2 = User.objects.create_user('user2','user2@email.ru','password')
        self.object_for_comment = self.user
        self.top_comment = Comments.objects.create(comment = "sdf", content_type = 
                                              ContentType.objects.get_for_model(self.object_for_comment),
                                              object_pk = self.object_for_comment.id, user = self.user )
        self.nested_comment = Comments.objects.create(comment = "sdf", content_type = 
                                              ContentType.objects.get_for_model(self.object_for_comment),
                                              object_pk = self.object_for_comment.id, user = self.user, 
                                              parent = self.top_comment)
        self.nested_comment_user2 = Comments.objects.create(comment = "sdf", content_type = 
                                              ContentType.objects.get_for_model(self.object_for_comment),
                                              object_pk = self.object_for_comment.id, user = self.user2, 
                                              parent = self.top_comment)
        self.top_comment_user2 = Comments.objects.create(comment = "sdf", content_type = 
                                              ContentType.objects.get_for_model(self.object_for_comment),
                                              object_pk = self.object_for_comment.id, user = self.user2 )

    def test_deep_delete(self):
        self.top_comment.deep_delete()
        count = Comments.objects.filter(id = self.top_comment_user2.id).count()
        self.assertEqual(count, 1)
        count = Comments.objects.filter(id__in = [self.top_comment.id, self.nested_comment.id,
                                                  self.nested_comment_user2.id]).count()
        self.assertEqual(count, 0)     

    def test_naming_urls(self):
        url = reverse('prospere_delete_comment_ajax')
        self.assertEqual(url,'/comments/delete_comment_ajax/')

    def test_getting_delete_comment(self):
        response = self.client.get(reverse('prospere_delete_comment_ajax'))
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.content,json.dumps({ 'success' : False, 'error' : 'wrong method' },sort_keys=True, indent=2))

    def test_deleting_top_comment_anonymous(self):
        post_data = get_comment_post_data(self.object_for_comment,is_user=True)
        post_data['comment_id'] = self.top_comment.id
        
    	response = self.client.post(reverse('prospere_delete_comment_ajax'), post_data)
        count = Comments.objects.filter(id = post_data['comment_id']).count()
        self.assertEqual(count, 1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, 
            json.dumps({ 'success' : False, 'error' : 'not authenticated' },sort_keys=True, indent=2))

    '''
    Deleting in my page. I am user
    '''
    def test_deleting_user2_top_comment(self):
        self.client.login(username='user',password='password')
        post_data = get_comment_post_data(self.object_for_comment,is_user=True)
        post_data['comment_id'] = self.top_comment_user2.id
        
    	response = self.client.post(reverse('prospere_delete_comment_ajax'), post_data)
        count = Comments.objects.filter(id = post_data['comment_id']).count()
        self.assertEqual(count, 0)
        count = Comments.objects.filter(id__in = [self.top_comment.id, self.nested_comment.id,
                                                  self.nested_comment_user2.id]).count()
        self.assertEqual(count, 3)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, json.dumps({ 'success' : True },sort_keys=True, indent=2))

    def test_deleting_my_top_comment_with_nested(self):
        self.client.login(username='user',password='password')
        post_data = get_comment_post_data(self.object_for_comment,is_user=True)
        post_data['comment_id'] = self.top_comment.id
        
    	response = self.client.post(reverse('prospere_delete_comment_ajax'), post_data)
        count = Comments.objects.filter(id = self.top_comment_user2.id).count()
        self.assertEqual(count, 1)
        count = Comments.objects.filter(id__in = [self.top_comment.id, self.nested_comment.id,
                                                  self.nested_comment_user2.id]).count()
        self.assertEqual(count, 0)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, json.dumps({ 'success' : True },sort_keys=True, indent=2))

    def test_deleting_user2_nested_comment(self):
        self.client.login(username='user',password='password')
        post_data = get_comment_post_data(self.object_for_comment,is_user=True)
        post_data['comment_id'] = self.nested_comment_user2.id
        
    	response = self.client.post(reverse('prospere_delete_comment_ajax'), post_data)
        count = Comments.objects.filter(id = post_data['comment_id']).count()
        self.assertEqual(count, 0)
        count = Comments.objects.filter(id__in = [self.top_comment.id, self.nested_comment.id,
                                                  self.top_comment_user2.id]).count()
        self.assertEqual(count, 3)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, json.dumps({ 'success' : True },sort_keys=True, indent=2))

    def test_deleting_my_nested_comment(self):
        self.client.login(username='user',password='password')
        post_data = get_comment_post_data(self.object_for_comment,is_user=True)
        post_data['comment_id'] = self.nested_comment.id
        
    	response = self.client.post(reverse('prospere_delete_comment_ajax'), post_data)
        count = Comments.objects.filter(id = post_data['comment_id']).count()
        self.assertEqual(count, 0)
        count = Comments.objects.filter(id__in = [self.top_comment.id, self.nested_comment_user2.id,
                                                  self.top_comment_user2.id]).count()
        self.assertEqual(count, 3)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, json.dumps({ 'success' : True },sort_keys=True, indent=2))

    '''
    Delete with absolute permission user2_comment for not auth.user model
    '''
    def test_deleting_user2_comment_for_object(self):
        self.object_for_comment = self.top_comment
        user2_comment = Comments.objects.create(comment = "sdf", content_type = 
                                  ContentType.objects.get_for_model(self.object_for_comment),
                                  object_pk = 1, user = self.user2 )
        self.client.login(username='user',password='password')
        post_data = get_comment_post_data(self.object_for_comment,is_user=True)
        post_data['comment_id'] = user2_comment.id      
    	response = self.client.post(reverse('prospere_delete_comment_ajax'), post_data)
        count = Comments.objects.filter(id = user2_comment.id).count()
        self.assertEqual(count, 0)  
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, json.dumps({ 'success' : True },sort_keys=True, indent=2))
    

    '''
    Deleting in not my page. I am user2
    '''
    def test_deleting_my_top_comment_without_nested(self):
        self.client.login(username='user2',password='password')
        post_data = get_comment_post_data(self.object_for_comment,is_user=True)
        post_data['comment_id'] = self.top_comment_user2.id
        
    	response = self.client.post(reverse('prospere_delete_comment_ajax'), post_data)
        count = Comments.objects.filter(id = post_data['comment_id']).count()
        self.assertEqual(count, 0)
        count = Comments.objects.filter(id__in = [self.top_comment.id, self.nested_comment.id,
                                                  self.nested_comment_user2.id]).count()
        self.assertEqual(count, 3)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, json.dumps({ 'success' : True },sort_keys=True, indent=2))

    def test_deleting_my_top_comment_with_nested(self):
        comment = Comments.objects.create(comment = "sdf", content_type = 
                                  ContentType.objects.get_for_model(self.object_for_comment),
                                  object_pk = self.object_for_comment.id, user = self.user2, parent = self.top_comment_user2 )
        self.client.login(username='user2',password='password')
        post_data = get_comment_post_data(self.object_for_comment,is_user=True)
        post_data['comment_id'] = self.top_comment_user2.id
        
    	response = self.client.post(reverse('prospere_delete_comment_ajax'), post_data)
        count = Comments.objects.filter(id = post_data['comment_id']).count()
        self.assertEqual(count, 1)
        count = Comments.objects.filter(id__in = [self.top_comment.id, self.nested_comment.id,
                                                  self.nested_comment_user2.id]).count()
        self.assertEqual(count, 3)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, json.dumps({ 'success' : False, 
            'error' : 'has child comments' },sort_keys=True, indent=2))

    def test_deleting_not_my_nested_comment_without_nested(self):
        self.client.login(username='user2',password='password')
        post_data = get_comment_post_data(self.object_for_comment,is_user=True)
        post_data['comment_id'] = self.nested_comment.id
        
    	response = self.client.post(reverse('prospere_delete_comment_ajax'), post_data)
        count = Comments.objects.filter(id = post_data['comment_id']).count()
        self.assertEqual(count, 1)
        count = Comments.objects.filter(id__in = [self.top_comment_user2.id, self.top_comment.id,
                                                  self.nested_comment_user2.id]).count()
        self.assertEqual(count, 3)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, json.dumps({ 'success' : False, 
            'error' : 'permission denied' },sort_keys=True, indent=2))

    def test_deleting_not_my_top_comment_with_nested(self):
        self.client.login(username='user2',password='password')
        post_data = get_comment_post_data(self.object_for_comment,is_user=True)
        post_data['comment_id'] = self.top_comment.id
        
    	response = self.client.post(reverse('prospere_delete_comment_ajax'), post_data)
        count = Comments.objects.filter(id = post_data['comment_id']).count()
        self.assertEqual(count, 1)
        count = Comments.objects.filter(id__in = [self.top_comment_user2.id, self.nested_comment.id,
                                                  self.nested_comment_user2.id]).count()
        self.assertEqual(count, 3)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, json.dumps({ 'success' : False, 
            'error' : 'permission denied' },sort_keys=True, indent=2))

