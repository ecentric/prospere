#coding: utf-8 
from django.shortcuts import render_to_response,redirect
from django.template import RequestContext
from django.views.generic.simple import direct_to_template

from prospere.contrib.cabinet.models import Documents
from prospere.contrib.cabinet.models import Storages
from prospere.contrib.account.models import Bookmarks
from django.contrib.contenttypes.models import ContentType

from django.views.decorators.cache import never_cache

from django.conf import settings
from django.core.urlresolvers import reverse

# WARNING : Documents.objects - all with hidden

@never_cache
def start_page(request, extra_context=None):
    
    context = {}
    if request.user.is_authenticated(): 
        path = request.get_full_path()
        st = path.find('?')
        sfx = ''
        if st != -1: sfx = path[st:]
        return redirect(reverse("prospere_user_page", kwargs={'username':request.user.username}) + sfx)

    from prospere.lib import handle_messages
    context['message'] = handle_messages(request)

    if not extra_context is None:
        for key, value in extra_context.items():
           context[key] = value
	
    return render_to_response('general/start.html',context,context_instance=RequestContext(request))

@never_cache
def search_results(request):
    from prospere.copia.views import make_document_list, make_user_list
    context = {}

    query = request.GET.get('query','')

    try:
        page = int(request.GET.get('page',1))
    except ValueError:
        page = 1

    if len(query)>2:
        per_page = getattr(settings,'NUMBER_SEARCH_RESULT_PER_PAGE', 10)

        from django.contrib.auth.models import User
        results = User.objects.filter(username__contains = query).order_by('username')
        users, num_pages = make_user_list(list(results),per_page=20,page=page)
        context['users'] = users

        results = Documents.search.query('*'+query+'*')
        documents, num_pages = make_document_list(list(results),per_page=per_page,page=page)
        context['documents'] = documents

        context['search_query'] = query
        context['num_pages'] = num_pages
        context['pages'] = range(1,context['num_pages']+1)
        context['current_page'] = page

    return render_to_response('general/search_results.html', context, context_instance=RequestContext(request))

@never_cache
def document(request,document_id):
    from prospere.contrib.comment import get_comment_form
    from prospere.contrib.cabinet.forms import VoteForm

    context = {}

    from prospere.lib import handle_messages
    from prospere.copia.views import humanize_path

    context['message'] = handle_messages(request)

    from django.core.exceptions import ObjectDoesNotExist
    try:
        document = Documents.objects.get(pk = document_id)
    except ObjectDoesNotExist:
        return direct_to_template(request,'error.html')

    if document.user != request.user and not document.is_shared: return direct_to_template(request,'error.html')

    context['document'] = document
    context['vote_form'] = VoteForm(initial={'id':document.id,
    										 'mark':document.mark,
    										 'count_vote':document.count_vote})
    context['user'] = document.user
    context['profile'] = document.user.get_profile()
    
    try:
        page = int(request.GET.get('page',1))
    except ValueError:
        page = 1
        
    context['document_path'] = humanize_path(document.path)

    context['content_type'] = ContentType.objects.get_for_model(document).id

    context['comment_form'] = get_comment_form(document, request)										 
    context['read_only_vote'] = document.user == request.user or ('document_votes' in request.session 
                                                                  and document.id in request.session['document_votes'])
    
    context['allow_get_file'] = getattr(settings,'ALLOW_GET_DOCUMENT_FILES', False)

    return render_to_response('general/document.html',context,context_instance=RequestContext(request))
    
@never_cache
def user_page(request, username):
    context = {}
    from django.contrib.auth.models import User
    from django.core.exceptions import ObjectDoesNotExist

    from prospere.lib import handle_messages
    context['message'] = handle_messages(request)

    my_page = False
    if request.user.is_authenticated() and request.user.username == username: 
        my_page = True
        context['user'] = request.user
        context['add_bookmark'] = False
    else:
        try:
            context['user'] = User.objects.get(username = username)
            # CHECK: if bookmark already added then add_bookmark = false else true
            context['add_bookmark'] = False
            if request.user.is_authenticated():
                count = Bookmarks.objects.filter(user = request.user, object = context['user'].id, type = 'UR').count()
                if not count: context['add_bookmark'] = True                
        except ObjectDoesNotExist:
            return direct_to_template(request,'error.html')

    context['profile'] = context['user'].get_profile()

    context['storage'] = Storages.objects.get(user = context['user']);

    from prospere.copia.views import make_document_list
    if my_page: documents = Documents.objects.filter(user = context['user']).order_by('-creation_date')[:3]
    else: documents = Documents.public_objects.filter(user = context['user']).order_by('-creation_date')[:3]
    context['documents'], num_pages = make_document_list(documents)

    from prospere.contrib.comment import get_comment_form
    context['content_type'] = ContentType.objects.get_for_model(context['user']).id
    context['comment_form'] = get_comment_form(context['user'], request)

    return render_to_response('general/user_page.html',context,context_instance=RequestContext(request))

def login(request,template_name):
    from django.contrib.sessions.models import Session
    from prospere.copia.models import SessionBonds
    from django.core.exceptions import ObjectDoesNotExist
    from django.contrib.auth import views
    from prospere.contrib.cabinet.models import Storages

    import time
    if request.method == 'POST':
        if not 'login_count' in request.session: request.session['login_count'] = 0 
        if not  'login_expire_time' in request.session : request.session['login_expire_time'] = 0
        if time.time() < request.session['login_expire_time']: return direct_to_template(request,'error.html')
        request.session['login_count'] += 1
        if request.session['login_count'] > 10:
            request.session['login_expire_time'] = time.time() + 60 * 60
            request.session['login_count'] = 0
            return direct_to_template(request,'error.html')

        content = views.login(request, template_name)

        if request.user.is_authenticated():
            try:
                bound = SessionBonds.objects.get(user = request.user)
                Session.objects.filter(session_key = bound.session_key).delete()
                bound.session_key = request.session.session_key
                bound.save()
            except ObjectDoesNotExist:
                SessionBonds.objects.create(user=request.user,session_key=request.session.session_key)

        return content
    return views.login(request, template_name)
