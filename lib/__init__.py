from message import *

class ContainerFkObjects(object):
    ''' 
    Get objects by foreign key
    '''
    def __init__(self, objects, fk, model_objects):
        self.fk_list = set()
        for item in objects:
            self.fk_list.add(getattr(item, fk))
        self.fk_objects = model_objects.filter(id__in = self.fk_list)
        self.objects_map = dict()
        for item in self.fk_objects:
            self.objects_map[item.id] = item
    def get_fk_object(self, fk):
        return self.get(fk)
    def get(self, fk):
        return self.objects_map[fk]
    def get_object_list(self):
        return self.fk_list

def set_get_argument(url,argument,value=""):
    st_index = url.rfind(argument+'=')

    if st_index == -1: 
        if '?' in url: return url+"&"+argument+'='+value
        else: return url+"?"+argument+'='+value

    f_index = url[st_index:].find('&')
    if f_index == -1: url = url[:st_index]+argument+'='+value
    else: url = url[:st_index]+url[st_index+f_index+1:]+'&'+argument+'='+value

    return url

'''
decorator
limit user access. Only for disseminator
'''
def disseminator_required(view_func):
    def wrapped_func(*args,**kwargs):
        from django.views.generic.simple import direct_to_template
        if args[0].session.get('is_disseminator',False):
            return view_func(*args,**kwargs)
        return direct_to_template(args[0],'error.html')
    return wrapped_func

def build_section_tree(storage_id, start_path='/'):

    from prospere.contrib.cabinet.models import Sections    

    def compare_sections(a,b):
        return cmp(a.caption, b.caption)
    def calc_depth(path):
        return path.count('/')

    from django.db.models import Q

    section_objects = Sections.objects.filter(Q(storage = storage_id), Q(path__startswith = start_path))

    sections = dict()
    for section in section_objects:
        if not sections.get(section.path,False): sections[section.path] = []
        section.depth = calc_depth(section.path)
        sections[section.path] += [section]
    for path,section in sections.items():
        sections[path].sort(compare_sections,reverse = True)

    class node(object):
        def __init__(self,section=None):
            self.section = section

    node_list = []
    path_stack = []
    current_path = start_path
    current_depth = calc_depth(start_path)
    while True:
        if current_path in sections and len(sections[current_path]): 
            s = sections[current_path].pop()

            path_stack.append(current_path)
            current_path = s.path + str(s.id) + '/'

            if current_depth < s.depth: 
                n = node()
                n.is_begin = True
                node_list.append(n)
            current_depth = s.depth

            n = node(s)
            n.is_section = True
            node_list.append(n)
        else:
            if len(path_stack): 
                current_path = path_stack.pop()
                depth = calc_depth(current_path)
                if current_depth > depth:
                    current_depth = depth
                    n = node()
                    n.is_end = True
                    node_list.append(n)
            else: break;

    return node_list

