from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
import datetime
from prospere.contrib.account.models import UserProfiles
from django.core.paginator import Paginator,EmptyPage,InvalidPage
from django.template.defaultfilters import date
import settings

COMMENT_MAX_LENGTH = getattr(settings,'COMMENT_MAX_LENGTH', 3000)

class Comment(object):
    '''
    Class that represent Comment
    '''
    def __init__(self, comment, user = False, profile = False):
        if user: 
            self.username = user.username
            self.user_id = user.id
            if not profile: profile = user.get_profile()
        else: self.username = comment.name
        self.text = comment.comment
        self.parent_id = comment.parent_id
        self.id = comment.id
        self.depth = comment.level
        self.date = date(comment.submit_date,"d b Y H:i:s")
        if profile:
            self.picture = profile.get_small_picture_url()
        else: self.picture = False

class CommentManager(models.Manager):

    def get_comment_list(self, object, per_page = None, page = 1):
        '''
        There are two ways to get heap of comments: 
        1. by instance of model(object receive queryset)
        2. by content_type and primary key(object receive dict like {ct:ct, pk:pk})
        '''
        if type(object) == dict:
            ct = object['ct']
            pk = object['pk']
        else:
            ct = ContentType.objects.get_for_model(object)
            pk = object.pk
        comments = self.filter(content_type = ct, object_pk = pk, level = 0).order_by('-submit_date')
        return self.make_comment_list(comments, per_page, page)

    def make_comment_list(self, comments, per_page = None, page = 1):
        from django.db.models import Q
        num_pages = 1
        if not per_page is None:
            paginator = Paginator(comments, per_page)
            try:
                pagin_page = paginator.page(page)
            except (EmptyPage,InvalidPage):
            	pagin_page = paginator.page(1)
            comments = pagin_page.object_list
            num_pages = paginator.num_pages
        comment_list = []

        tree_id_list = []
        for comment in comments:
            tree_id_list.append(comment.tree_id)
            
        nested_comments = []
        if len(comments) > 0:
            nested_comments = self.filter(Q(content_type = comments[0].content_type_id) &
                                  Q(object_pk = comments[0].object_pk) & Q(tree_id__in = tree_id_list) & 
                                  ~Q(level = 0)).order_by('submit_date')
        comments = list(comments)
        comments.extend(nested_comments)

        user_id_list = set()
        for comment in comments:
            if not comment.user_id is None:
                user_id_list.add(comment.user_id)
                
        users = User.objects.filter(pk__in = user_id_list)
        profiles = UserProfiles.objects.filter(user__in = user_id_list)
        def get_user(id):
            if id is None: return False
            for user in users:
        	    if user.id == id: return user
            return False
        def get_profile(id):
            if id is None: return False
            for profile in profiles:
        	    if profile.user_id == id: return profile
            return False

        for comment in comments:
            user = get_user(comment.user_id)
            profile = get_profile(comment.user_id)
            comment_list.append(Comment(comment, user, profile))
            
        return comment_list, num_pages


class Comments(MPTTModel):
    '''
    Model for store tree comments
    '''
    content_type =  models.ForeignKey(ContentType)
    object_pk      = models.BigIntegerField()
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")

    parent = TreeForeignKey('self', null = True, blank = True, related_name = 'children')
    
    user = models.ForeignKey(User, blank = True, null=True)
    name = models.CharField(max_length = 20,blank = True)
    comment = models.TextField(max_length=COMMENT_MAX_LENGTH)
    submit_date = models.DateTimeField(default=datetime.datetime.now)
    
    is_moderate   = models.BooleanField(default=False)
    is_removed  = models.BooleanField(default=False)
    
    objects = CommentManager()

    class Meta:
        ordering = ["submit_date"]

    def __unicode__(self):
        return str(self.user)+'('+self.name+') - '+self.comment

    def deep_delete(self):
        comment_objects = Comments.objects.filter(tree_id = self.tree_id, level__gt = self.level)
        comments = dict();
        for comment in comment_objects:
            comments[comment.parent_id] = comment

        delete_list = set()
        comment = self
        while(comment):
            delete_list.add(comment.id)
            comment = comments.get(comment.id, False)
        Comments.objects.filter(id__in = delete_list).delete()

