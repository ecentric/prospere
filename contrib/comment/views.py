from django.views.decorators.http import require_POST
from django.shortcuts import redirect
from django.http import HttpResponse
from forms import CommentForm, BondCommentForm, CommentSecurityForm
from models import Comments
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.views.generic.simple import direct_to_template

from models import Comment

def json_response(x):
    import json
    return HttpResponse(json.dumps(x, sort_keys=True, indent=2),
                        content_type='application/json; charset=UTF-8')

# not view function
def handle_comment(request):
   
    if request.method != 'POST':
        return { 'success' : False, 'error' : 'wrong method' }
        
    if not request.user.is_authenticated(): 
        return { 'success' : False, 'error' : 'user not authentificated' }

    form = BondCommentForm(data = request.POST)
    name = ''
    user_id = request.user.id

    if form.is_valid():
    	cd = form.cleaned_data
        if cd['comment_id'] is None: parent = None
        else: parent = Comments.objects.get(id = cd['comment_id'])
    	
    	ctype = cd['content_type']

        (app_label, model) = ctype.split(".", 1)
    	ctype = ContentType.objects.get_by_natural_key(app_label, model)
    	comment = Comments.objects.create(content_type = ctype, object_pk = cd['object_pk'], name = name, user_id = user_id,
                                          comment = cd['comment'], parent = parent)
        return { 'success' : True , 'comment' : comment}
    return { 'success' : False, 'error' : str(form.errors) }

def post_comment(request):
    from prospere.lib import set_get_argument
    state = handle_comment(request)
    if state['success']:
        redirect_to = request.REQUEST.get('next', '/')
        redirect_to = set_get_argument(redirect_to,"message","comment_saved")
        return redirect(redirect_to)
    else: return direct_to_template(request,'error.html')
        
def post_comment_ajax(request):
    state = handle_comment(request)
    if state['success']:
        comment = None
        if request.user.is_authenticated(): comment = Comment(state['comment'], request.user)
        else: comment = Comment(state['comment'])
        return json_response({ 'success' : True, 'comment' : comment.__dict__})
    else: return json_response(handle_comment(request))

def edit_comment_ajax(request):
    '''
    form field parent is current modified comment
    '''
    if request.method != 'POST':
        return json_response({ 'success' : False, 'error' : 'wrong method' })
    if not request.user.is_authenticated(): return json_response({ 'success' : False, 'error' : 'not authenticated' })
    form = BondCommentForm(data = request.POST)
    if form.is_valid():
        comment = Comments.objects.get(id = form.cleaned_data['comment_id'])
        if comment.user != request.user: return json_response({ 'success' : False, 'error' : 'permission denied' })
        count = Comments.objects.filter(parent = comment).count()
        if count != 0: return json_response({ 'success' : False, 'error' : 'has child comments' })
        comment.comment = form.cleaned_data['comment']
        comment.save()
        return json_response({ 'success' : True })
    return json_response({ 'success' : False, 'error' : 'wrong form fields' })

def delete_comment_ajax(request):
    if request.method != 'POST':
        return json_response({ 'success' : False, 'error' : 'wrong method' })
    if not request.user.is_authenticated(): return json_response({ 'success' : False, 'error' : 'not authenticated' })
    form = CommentSecurityForm(data = request.POST)

    if form.is_valid():
        absolute_permission = False
        if form.cleaned_data['content_type'] == 'auth.user':
            if int(form.cleaned_data['object_pk']) == request.user.id: absolute_permission = True
        else: 
            model = models.get_model(*form.cleaned_data['content_type'].split(".", 1))
            obj = model.objects.get(pk = int(form.cleaned_data['object_pk']))
            if hasattr(obj, 'user') and obj.user == request.user: absolute_permission = True

        comment = Comments.objects.get(id = form.cleaned_data['comment_id'])       
        if not absolute_permission:     
            if comment.user != request.user: return json_response({ 'success' : False, 'error' : 'permission denied' })
            count = Comments.objects.filter(parent = comment).count()
            if count != 0: return json_response({ 'success' : False, 'error' : 'has child comments' })

        comment.deep_delete()
        return json_response({ 'success' : True })

    return json_response({ 'success' : False, 'error' : 'wrong form fields' })    

def get_comment_tree(request, content_type, object):
    '''
    json view for get heap of comments by content_type_id, object_pk and page (as get param)
    '''
    from django.conf import settings
    try:
        page = int(request.GET.get('page',1))
    except ValueError:
        page = 1

    per_page = getattr(settings, 'NUMBER_COMMENT_PER_PAGE', 10)
    comment_list, num_pages = Comments.objects.get_comment_list({ 'ct' : content_type, 'pk' : object}, 
                                    per_page = per_page, page = page)

    js_comment_list = []
    for comment in comment_list:
        js_comment_list.append(comment.__dict__)
    return json_response({ 'success' : True, 'page' : page, 'heap_comments' : js_comment_list, 'num_pages' : num_pages })

