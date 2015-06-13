from general import start_page
from django.core.paginator import Paginator,EmptyPage,InvalidPage
from django.contrib.auth.models import User
from prospere.contrib.cabinet.models import Sections
from prospere.contrib.account.models import UserProfiles
from prospere.lib import ContainerFkObjects

def csrf_failure(request, reason=""):
    from django.views.generic.simple import direct_to_template
    return direct_to_template(request,"csrf_failure.html")

class PathContainer(object):
    def __init__(self):
        self.section_ids = set()

    def add_path(self,path):
        for item in path[1:-1].split('/'):
            self.section_ids.add(item)

    def make_query(self):
        self.sections = Sections.objects.filter(pk__in = self.section_ids)

    def get_humanize_path(self,path):
        item_list = [int(item) for item in path[1:-1].split('/')]

        class section:
            def __init__(self,id,caption):
                self.id = id
                self.caption = caption

        def get_caption(id):
            for section in self.sections:
                if section.id == id: return section
            return str(id)

        hum_path = list()
        for id in item_list:
            hum_path.append(section(id, get_caption(id) ))

        return hum_path

def humanize_path(path):
    '''
    return dict - section.pk : section.caption
    '''        
    if path == '/' :
        return []
        
    path_container = PathContainer()
    path_container.add_path(path)
    path_container.make_query() 
    return path_container.get_humanize_path(path)

def get_page_objects(objects, per_page = None, page = 1):
    num_pages = 1
    if not per_page is None:
        paginator = Paginator(objects,per_page)
        try:
            pagin_page = paginator.page(page)
        except (EmptyPage,InvalidPage):
        	pagin_page = paginator.page(1)
        objects = pagin_page.object_list
        num_pages = paginator.num_pages
    return objects, num_pages

class pDocument(object):
    def __init__(self, document, user, path):
        self.username = user.username
        self.user_id = user.id

        self.description = document.description
        self.id = document.id
        self.title = document.title
        self.path = path
        self.file_size = document.file_size
        self.creation_date = document.creation_date
        self.file_url = document.get_file_url()
class pUser(object):
    def __init__(self, user, profile):
        self.username = user.username
        self.user_id = user.id

        #self.count_vote = profile.count_vote
        #self.mark = profile.mark
        #self.description = profile.description
class pBookmark(object):
    def __init__(self, bookmark, profile, user):
        self.object_id = bookmark.object
        self.name = user.username
        self.picture = profile.small_picture

def make_document_list(documents, per_page = None, page = 1):

    documents, num_pages = get_page_objects(documents,per_page,page)
    document_list = []
    
    path_container = PathContainer()
    user_id_list = set()
    for document in documents:
        user_id_list.add(document.user_id)
        path_container.add_path(document.path)
    
    path_container.make_query()        
    users = User.objects.filter(pk__in = user_id_list)

    def get_user(id):
        for user in users:
    	    if user.id == id: return user
    	return False
    for document in documents:
    	user = get_user(document.user_id)
        document_list.append(pDocument(document,user,
                                           path_container.get_humanize_path(document.path)))
        
    return document_list,num_pages


def make_user_list(users,per_page=None,page=1):

    users, num_pages = get_page_objects(users,per_page,page)
    user_list = []
    '''
    id_list = set()
    for user in users:
        id_list.add(user.id)
    profiles = UserProfiles.objects.filter(user__in = id_list)
    def get_profile(user_id):
        for profile in profiles:
            if (profile.user_id == user_id): 
                return profile

    for user in users:
        user_list.append(pUser(user,get_profile(user.id)))        
    return user_list,num_pages
    '''
    return users, num_pages

def make_bookmark_list(user_id):
    from prospere.contrib.account.models import Bookmarks
    bookmarks = Bookmarks.objects.filter(user = user_id)
    id_list = set()
    for bmrk in bookmarks:
        id_list.add(bmrk.object)
    users = User.objects.filter(id__in = id_list)
    profiles = UserProfiles.objects.filter(user__in = id_list)
    def get_profile(user_id):
        for profile in profiles:
            if (profile.user_id == user_id): 
                return profile
    def get_user(user_id):
        for user in users:
            if (user.id == user_id): 
                return user
    bmrk_list = []
    for bookmark in bookmarks:
        bmrk_list.append({ 'object_id' : bookmark.object, 
                           'name' : get_user(bookmark.object).username,
                           'picture' : get_profile(bookmark.object).get_small_picture_url() })
    #pBookmark(bookmark,get_profile(bookmark.user_id),get_user(bookmark.user_id)))
    return bmrk_list

def make_sales_list(user,per_page=None,page=1):

    from datetime import datetime
    # 3 month report
    now_date = datetime.now()
    year = now_date.year
    month = now_date.month - 2
    if month <= 0:
        month += 12
        year -= 1
    st_date = datetime(year,month,1)

    deals = user.selling_set.filter(state = 'PD',date__gte = st_date ).order_by('-date')

    deals, num_pages = get_page_objects(deals,per_page,page)

    class MonthDeals():
        def __init__(self,month,deals,total):
            self.month = month
            self.deals = deals
            self.total = total

    from django.db.models import Sum
    def calc_month_total(month):
        return user.selling_set.filter(state = 'PD',date__month = month).aggregate(total=Sum('cost'))['total']  

    from prospere.contrib.cabinet.models import Documents
    container = ContainerFkObjects(deals,'product_id',Documents.all_objects)

    report = list()
    if len(deals):
        current_month = deals[0].date.month
        month_deals = list()
        total = 0
        for deal in deals:
            if current_month != deal.date.month:
                report.append(MonthDeals(current_month,month_deals,calc_month_total(current_month)))
                current_month = deal.date.month
                month_deals = list()
                total = 0
            document = container.get_fk_object(deal.product_id)
            deal.product_title = document.title
            deal.document_is_removed = document.is_removed
            month_deals.append(deal)
            total += deal.cost
        report.append(MonthDeals(current_month,month_deals,calc_month_total(current_month)))

    return report, num_pages

