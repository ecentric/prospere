#coding: utf-8 
from django.shortcuts import render_to_response,redirect
from django.http import HttpResponse
from django.views.generic.simple import direct_to_template
from django.template import RequestContext

from ..forms import AddDocumentForm, EditDocumentForm
from ..models import Documents, Sections, Storages
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from prospere.lib import set_get_argument

from django.core.files.storage import default_storage
from django.utils.html import strip_tags

import time
from hashlib import md5
from django.conf import settings
import os
permissions = getattr(settings,'FILE_UPLOAD_PERMISSIONS')

unsafe_ext = ['.exe','.com','.pif','.bat','.scr']

def json_response(x):
    import json
    return HttpResponse(json.dumps(x, sort_keys=True, indent=2),
                        content_type='application/json; charset=UTF-8')

def calc_owner(path):
    if path == '/': return ''
    else: return path[path[:-1].rindex('/')+1:]
def calc_owner_id(path):
    if path == '/': return False
    else: return int(path[path[:-1].rindex('/')+1:-1])
def strip_description(descr):
    descr = descr.replace('&nbsp;',' ')
    return strip_tags(descr)
'''
Add document view
'''
@login_required(redirect_field_name='next')
@never_cache
def add_document(request, section):
    '''
    Views for Add document
    '''    
    section_object = Sections.objects.get(pk = section)
    storage = request.user.storages_set.get()
    if section_object.storage != storage:
        return direct_to_template(request,'error.html')
    path = section_object.path + section +'/'

    context = {}
    if request.method == 'POST':
        redirect_to = request.GET.get('next', '/')
        node_anchor = '#'+request.GET.get('node_anchor', '')
        
        form = AddDocumentForm(request.POST,request.FILES)
        if form.check(request, storage):
            cd = form.cleaned_data
            
            filename = cd['file'] #handle_document_file(cd['file'])
            if not filename: return direct_to_template(request,'error.html')

            if not storage.is_store: cd['is_free'] = True
            if cd['is_free']: cost = '0.00'
            else: cost = cd['cost']
            Documents.objects.create(path = path, title = cd['title'], 
    		                         html_description = cd['html_description'], 
    		                         description = strip_description(cd['html_description']),
    		                         user = request.user, 
                                     file_size = cd['file'].size,
                                     storage = storage, file = filename,
                                     is_free = cd['is_free'], cost = cost)

            redirect_to = set_get_argument(redirect_to,"message","cabinet_document_saved")+node_anchor
            return redirect(redirect_to)
    else:
        form = AddDocumentForm(initial={'title' : '',
                                        'html_description' : '',
                                        'is_free' : True,
                                        'cost':'0.00' })
    
    context['mem_state'] = storage.mem_limit - storage.mem_busy
    context['storage'] = storage
    context['form'] = form
    context['is_free'] = form['is_free'].value()
    return render_to_response('add_document.html',context,context_instance=RequestContext(request))
'''
Edit document view
'''
@login_required(redirect_field_name='next')
@never_cache
def edit_document(request, document_id):
    context = {}

    document = Documents.objects.get(id = document_id)
    storage = request.user.storages_set.get()

    if document.user_id == request.user.id:
        if request.method == 'POST':
            redirect_to = request.GET.get('next', '/')
            node_anchor = '#'+request.GET.get('node_anchor', '')
            
            form = EditDocumentForm(request.POST,request.FILES)
            if form.check(request, storage, document.file_size):
                cd = form.cleaned_data
                
                if document.is_free and cd['file']:
                    old_file_size = document.file_size
                    document.delete_file()

                    document.file = cd['file']
                    document.file_size = cd['file'].size
                    storage.mem_busy += cd['file'].size - old_file_size
                    storage.save()

                if not document.is_free and cd['cost'] and storage.is_store:
                    document.cost = cd['cost']

                document.title = cd['title']
                document.html_description = cd['html_description']
                document.description = strip_description(cd['html_description'])

                document.save()
                redirect_to = set_get_argument(redirect_to,"message","cabinet_document_saved")+node_anchor
                
                return redirect(redirect_to)
        else:
            form = EditDocumentForm(initial = {'title' : document.title,
                                               'html_description' : document.html_description,
                                               'cost' : document.cost })
        context['mem_state'] = storage.mem_limit - storage.mem_busy + document.file_size
        context['form'] = form
        context['is_free'] = document.is_free
        return render_to_response('edit_document.html',context,
                                  context_instance=RequestContext(request))
    return direct_to_template(request,'error.html')

@login_required(redirect_field_name='next')
def change_document_access(request):
    if request.method == 'POST':
        id = request.POST.get('id',False)
        if not id: return json_response({ 'success' : False, 'error' : 'missing id' })
        document = Documents.objects.get(id = id)
        if document.user_id != request.user.id: 
            return json_response({ 'success' : False, 'error' : 'permission denied' })

        if document.is_shared:
            document.hide()
        else:
            parent_id = calc_owner_id(document.path)
            if parent_id:
                owner = Sections.objects.get(id = parent_id)
                if not owner.is_shared: return json_response({ 'success' : False, 'error' : 'owner not shared' })
            document.share()

        return json_response({ 'success' : True })
    return json_response({ 'success' : False, 'error' : 'wrong method' })

@login_required(redirect_field_name='next')
def delete_document(request):

    if request.method == 'POST':
        document_id = request.POST.get('document_id',False)
        if not document_id: return direct_to_template(request,'error.html')

        document = Documents.objects.get(pk = document_id)

        if document.user_id == request.user.id:
            if document.last_purchase is None:
                document.delete(request = request) # change  mem_busy and delete file
            else:
                document.is_removed = True
                document.storage.mem_busy -= document.file_size
                document.storage.save()
                document.save()

            return json_response({ 'success' : True })

        return json_response({ 'success' : False, 'error' : 'not own document' })

    return json_response({ 'success' : False, 'error' : 'wrong method' })

