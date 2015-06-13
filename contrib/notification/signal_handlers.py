#coding: utf-8 
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from models import Notifications
from prospere.contrib.account.models import Bookmarks, UserProfiles
from prospere.contrib.cabinet.models import Documents
from prospere.contrib.comment.models import Comments

from prospere.lib import ContainerFkObjects
from django.core.mail.message import EmailMessage
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.template.loader import render_to_string

def get_user_profiles(bookmarks):
    user_id_list = set()
    for bookmark in bookmarks:
        user_id_list.add(bookmark.user_id)
    user_profiles_objects = UserProfiles.objects.only('user', 'document_notif_on' ).filter(
            user__in = user_id_list)
    profiles = dict()
    for profile in user_profiles_objects:
        profiles[profile.user_id] = profile
    return profiles

#TODO: TEST
def send_document_notif(bookmarks, document):
    users = ContainerFkObjects(bookmarks, 'user_id', User.objects)
    profiles = get_user_profiles(bookmarks)

    emails = list()
    for bookmark in bookmarks:
        if profiles[bookmark.user_id].document_notif_on:
            emails += [users.get(bookmark.user_id).email]

    if len(emails) > 0:
        site = Site.objects.get_current()
        ctx_dict = { 'document_title' : document.title,
                     'document_username' : document.user.username,
                     'link' : reverse('prospere_document', kwargs = {'document_id' : document.id}),
                     'site': site }
        text = render_to_string('new_document_email', ctx_dict)

        message = EmailMessage(u'Новый файл', text, u'management@copia.org.ua', bcc = emails) 
        message.content_subtype = "html"
        message.send()

def save_document(sender, **kwargs):

    document = kwargs['instance']
    username = document.user.username
    if document.is_shared:
        #WARN: Document already exist
        #TODO: TEST
        old_document = Documents.objects.get(id = document.id)
        if old_document.is_shared == document.is_shared: return

        bookmarks = Bookmarks.objects.filter(object = document.user_id)
        #send_document_notif(bookmarks, document)
        for bookmark in bookmarks:
            Notifications.objects.create(user_id = bookmark.user_id, username = username, action = 'AD',  
                                         content_object = document)
    else:
        ctype = ContentType.objects.get_for_model(document)
        Notifications.objects.filter(object_pk = document.id, content_type = ctype).delete()

def deleted_document(sender, **kwargs):

    document = kwargs['instance']
    ctype = ContentType.objects.get_for_model(document)
    Notifications.objects.filter(object_pk = document.id, content_type = ctype).delete()    

def created_comment(sender, **kwargs):

    if kwargs['created']:
        comment = kwargs['instance']

        username = comment.user.username
        content_object = comment.content_object

        if type(content_object) == Documents: user_id = content_object.user_id
        elif type(content_object) == User: user_id = content_object.id
        else: return

        if comment.user_id != user_id:
            Notifications.objects.create(user_id = user_id, username = username, action = 'AC', 
                                         content_object = comment)

        if not comment.parent is None and comment.parent.user_id != user_id and comment.parent.user_id != comment.user_id:
            Notifications.objects.create(user_id = comment.parent.user_id, username = username, action = 'AC', 
                                             content_object = comment)

def deleted_comment(sender, **kwargs):

    comment = kwargs['instance']
    ctype = ContentType.objects.get_for_model(comment)
    Notifications.objects.filter(content_type = ctype, object_pk = comment.id).delete()

models.signals.pre_save.connect(save_document, sender = Documents)
models.signals.pre_delete.connect(deleted_document, sender = Documents)
models.signals.post_save.connect(created_comment, sender = Comments)
models.signals.pre_delete.connect(deleted_comment, sender = Comments)

