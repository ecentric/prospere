#coding: utf-8 
from models import Notifications
from django.http import HttpResponse
from prospere.contrib.cabinet.models import Documents
from prospere.contrib.comment.models import Comments
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.html import escape

def crop(string ,count = 40):
    if len(string) > count:
        string = string[:count - 3] + '...'
    return string

from django.contrib.contenttypes.models import ContentType

def make_notifications_list(notifications):
    nl = []

    document_id_list = set()
    comment_id_list = set()
    for notification in notifications:
        if notification.action == 'AD':
            document_id_list.add(notification.object_pk)
        if notification.action == 'AC':
            comment_id_list.add(notification.object_pk)


    document_objects = Documents.objects.only('title', 'id').filter(id__in = document_id_list)
    documents = dict()
    for document in document_objects:
        documents[document.id] = document

    comment_objects = Comments.objects.filter(id__in = comment_id_list)
    comments = dict()
    user_id_list = set()
    for comment in comment_objects:
        comments[comment.id] = comment
        if ContentType.objects.get_for_id(comment.content_type_id).natural_key() == ('auth', 'user'):
            user_id_list.add(comment.object_pk)

    user_objects = User.objects.only('username').filter(id__in = user_id_list)
    users = dict()
    for user in user_objects:
        users[user.id] = user

    for notification in notifications:
        json_notif = {'id' : notification.id,
                      'username' : notification.username,
                      'action' : notification.get_action_display(),
                      'action_type' : notification.action,
                      'object_id' : notification.object_pk, }

        if notification.action == 'AD':
            json_notif['link'] = reverse('prospere_document', kwargs = { 'document_id' :  notification.object_pk }), 
            json_notif['text'] = escape(documents[notification.object_pk].title)

        if notification.action == 'AC':
            comment = comments[notification.object_pk]
            k = ContentType.objects.get_for_id(notification.content_type_id).natural_key() 
            if ContentType.objects.get_for_id(comment.content_type_id).natural_key() == ('cabinet', 'documents'):
                json_notif['link'] = reverse('prospere_document', 
                                             kwargs = { 'document_id' :  comment.object_pk }),
            else:
                json_notif['link'] = reverse('prospere_user_page', 
                                             kwargs = { 'username' :  users[comment.object_pk].username }),
            json_notif['text'] = escape(crop(comment.comment))

        nl.append(json_notif)
    return nl

def json_response(x):
    import json
    return HttpResponse(json.dumps(x, sort_keys = True, indent = 2),
                        content_type = 'application/json; charset=UTF-8')

def get_notifications(request):
    if not request.user.is_authenticated():
        return json_response({ 'success' : False, 'error' : 'user not authentificated' })    
    nl = make_notifications_list(Notifications.objects.filter(user = request.user).order_by('-creation_date')[:10])
    return json_response({ 'success' : True, 'notifications' : nl })
    
def delete_notification(request):
    if not request.method == 'POST': 
        return json_response({ 'success' : False, 'error' : 'wrong method' })
    if not request.user.is_authenticated():
        return json_response({ 'success' : False, 'error' : 'user not authentificated' })
    id = request.POST.get('id', False)
    if id == False:
        return json_response({ 'success' : False, 'error' : 'missing id' })
    id = int(id)
    notif = Notifications.objects.get(id = id)
    if notif.user_id != request.user.id:
        return json_response({ 'success' : False, 'error' : 'not own' })
    notif.delete()
    return json_response({ 'success' : True })

