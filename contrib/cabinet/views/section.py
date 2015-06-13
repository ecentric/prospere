#coding: utf-8 
from django.shortcuts import render_to_response,redirect
from django.views.generic.simple import direct_to_template
from django.template import RequestContext
from django.http import HttpResponse

from prospere.contrib.cabinet.forms import AddSectionForm
from prospere.contrib.cabinet.models import Documents
from prospere.contrib.cabinet.models import Sections, Storages

from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from prospere.lib import set_get_argument

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
def path_depth(path):
    return path.count('/')-1   

@login_required(redirect_field_name='next')
@never_cache
def add_section(request):
    from django.conf import settings
    max_depth = getattr(settings,'MAX_PATH_DEPTH')
    if request.method == 'POST':
        form = AddSectionForm(request.POST)
        if form.is_valid():

            owner_section = request.POST.get('owner_section', False)
            if not owner_section:owner_section = ''
            storage_id = request.POST.get('storage', False)
            if not storage_id: return json_response({ 'success' : False, 'error' :'missing storage_id' })
            storage_id = int(storage_id)
            storage = request.user.storages_set.get()
            if storage_id != storage.id: return json_response({ 'success' : False, 'error' :'permission denied' })

            if owner_section:
                section = Sections.objects.get(pk = owner_section)
                if section.storage_id != storage_id:
                    return json_response({ 'success' : False, 'error' : 'wrong owner section id' })
                current_path = section.path + owner_section + '/'
            else: 
                current_path = '/'
            if path_depth(current_path) >= max_depth: return json_response({ 'success' : False,
                                                                             'error' : 'depth is to large' })
            
            section = Sections.objects.create(storage_id = storage_id, caption = form.cleaned_data['section_caption'],
                                    path = current_path)

            return json_response({ 'success' : True, 'id' : section.id })

        return json_response({ 'success' : False, 'error' : 'not valid params' })
    return json_response({ 'success' : False, 'error' : 'wrong method' })

@login_required(redirect_field_name='next')
@never_cache
def edit_section(request):

    if request.method == 'POST':
        section_id = request.POST.get('section_id',False)
        if not section_id: return json_response({ 'success' : False, 'error' : 'missing id' })
        section = Sections.objects.get(pk = section_id)

        if section.storage.user_id != request.user.id:   
            return json_response({ 'success' : False, 'error' : 'not own section' })

        #current_path = section.path + str(section.id) + '/'

        form = AddSectionForm(request.POST)
        if form.is_valid():
            section.caption = form.cleaned_data['section_caption']
            section.save()

            return json_response({ 'success' : True })
        return json_response({ 'success' : False, 'error' : 'missing caption' })

    return json_response({ 'success' : False, 'error' : 'wrong method' })

@login_required(redirect_field_name='next')
def change_section_access(request):
    if request.method == 'POST':
        id = request.POST.get('id',False)
        if not id: return json_response({ 'success' : False, 'error' : 'missing id' })
        section = Sections.objects.get(id = id)
        if section.storage.user_id != request.user.id: 
            return json_response({ 'success' : False, 'error' : 'permission denied' })

        if section.is_shared:
            path = section.path + str(section.id) + '/'
            Sections.objects.filter(path__startswith = path).update(is_shared = False)
            documents = Documents.objects.filter(path__startswith = path)
            for doc in documents:
                if doc.is_shared: doc.hide()
            section.is_shared = False
            section.save()            
        else:
            parent_id = calc_owner_id(section.path)
            if parent_id:
                owner = Sections.objects.get(id = parent_id)
                if not owner.is_shared: return json_response({ 'success' : False, 'error' : 'owner not shared' })
            section.is_shared = True
            section.save()

        return json_response({ 'success' : True })
    return json_response({ 'success' : False, 'error' : 'wrong method' })

@login_required(redirect_field_name='next')
def delete_section(request):

    if request.method == 'POST':
        section_id = request.POST.get('section_id',False)
        if not section_id: return json_response({ 'success' : False, 'error' : 'missing id' })

        section = Sections.objects.get(id = section_id)
        if section.storage.user_id == request.user.id:   
            current_path = section.path + section_id + '/'

            redirect_to = request.POST.get('next', '/')

            count_child_sections = Sections.objects.filter(path=current_path).count()
            if count_child_sections: return json_response({ 'success' : False, 'error' : 'not empty' })

            count_child_documents = Documents.objects.filter(path=current_path).count()
            if count_child_documents: return json_response({ 'success' : False, 'error' : 'not empty' })

            section.delete()

            return json_response({ 'success' : True })
        return json_response({ 'success' : False, 'error' : 'not own' })

    return json_response({ 'success' : False, 'error' : 'wrong method' })


