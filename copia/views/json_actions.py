from django.http import HttpResponse

from prospere.contrib.cabinet.models import Documents
from prospere.contrib.cabinet.models import Sections, Storages
from django.views.decorators.cache import never_cache

def json_response(x):
    import json
    return HttpResponse(json.dumps(x, sort_keys=True, indent=2),
                        content_type='application/json; charset=UTF-8')

# WARNING : Documents.objects - all with hidden
@never_cache
def vote(request):
    from prospere.contrib.cabinet import vote_document
    from prospere.contrib.account import vote_user
    from prospere.contrib.account.models import UserProfiles
    #from cabinet import vote_document
    from django.utils import simplejson
    if request.method == 'POST':
        
        document_id = request.POST.get('id',False)
        score = request.POST.get('score',False)
        if not document_id or not score:
            json = simplejson.dumps({'state':'ERROR'})
            return HttpResponse(json)
    
        document_id = int(document_id)
        if not 'document_votes' in request.session: request.session['document_votes'] = list()
        if document_id in request.session['document_votes']:
            json = simplejson.dumps({'state' : 'ERROR'})
            return HttpResponse(json)
        
        request.session['document_votes'].append(document_id)
        request.session.modified = True

        document = Documents.objects.get(id = int(document_id))
        vote_document(document, score)
        vote_user(document.user_id, score)
        json = simplejson.dumps({'state':'OK'})
        return HttpResponse(json)

@never_cache
def get_storage_tree(request):

    from django.utils import simplejson
    storage = request.GET.get('storage_id',False)

    if not storage: return json_response({ 'success' : False, 'errors' : 'storage_id missed' })
    storage =  Storages.objects.get(id = int(storage))
    my_storage = False
    if storage.user == request.user:
        my_storage = True
        section_objects = Sections.objects.filter(storage = storage)
        documents = Documents.objects.filter(storage = storage)
    else:
        section_objects = Sections.public_objects.filter(storage = storage)
        documents = Documents.public_objects.filter(storage = storage)

    def calc_depth(path):
        return path.count('/')            
    def calc_parent(path):
        if path == '/': return 0
        else: return path[path[:-1].rfind('/')+1:-1]

    heap_nodes = []
    for section in section_objects:
        heap_nodes.append({'name' : section.caption,
                           'is_dir' : True,
                           'is_shared' : section.is_shared,
                           'id' : section.id,
                           'parent' : calc_parent(section.path),
                           'depth' : calc_depth(section.path)})
    #mem_busy = 0
    for document in documents:
        heap_nodes.append({'name' : document.title,
                           'is_dir' : False,
                           'is_shared' : document.is_shared,
                           'id' : document.id,
                           'file_size' : document.file_size,
                           'parent' : calc_parent(document.path),
                           'depth' : calc_depth(document.path)})
        #mem_busy += document.file_size

    return json_response({ 'success' : True,
                           'nodes' : heap_nodes,'mem_busy' : storage.mem_busy, 'is_my_storage' : my_storage })

