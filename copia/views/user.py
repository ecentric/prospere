from django.shortcuts import render_to_response,redirect
from django.template import RequestContext
from django.views.generic.simple import direct_to_template

from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

from prospere.contrib.cabinet.models import Documents, Sections, Storages

from prospere.lib import build_section_tree, disseminator_required

def path_depth(path):
    return path.count('/')-1
# Account; profile
@login_required(redirect_field_name='next')
def change_profile(request):
    context = {}

    from prospere.lib import handle_messages
    context['message'] = handle_messages(request)

    from prospere.contrib.account.forms import ChangeProfile
    form = ChangeProfile()
    context['form']=form;
    
    return render_to_response('user/profile.html',context,context_instance=RequestContext(request))

@never_cache
@login_required(redirect_field_name='next')
def sales(request):
    context = {}

    try:
        page = int(request.GET.get('page',1))
    except ValueError:
        page = 1

    from prospere.copia.views import make_sales_list
    report, num_pages = make_sales_list(request.user,per_page = 50,page=page)

    context['num_pages'] = num_pages
    context['pages'] = range(1,context['num_pages']+1)
    context['current_page'] = page

    context['report'] = report
    return render_to_response('user/sales.html',context,context_instance=RequestContext(request))    

@login_required(redirect_field_name='next')
def my_purchases(request):
    context = {}

    from prospere.lib import handle_messages, ContainerFkObjects
    context['message'] = handle_messages(request)

    purchases = request.user.purchase_set.filter(state__in = ['WP','PD']).order_by('date')

    container = ContainerFkObjects(purchases,'product_id',Documents.all_objects)
    for purchase in purchases:
        document = container.get_fk_object(purchase.product_id)
        purchase.product_title = document.title
        purchase.document_is_removed = document.is_removed
    context['purchases'] = purchases
    return render_to_response('user/purchases.html',context,context_instance=RequestContext(request))

@login_required(redirect_field_name='next')
def basket(request):
    context = {}

    from prospere.lib import handle_messages, ContainerFkObjects
    context['message'] = handle_messages(request)

    orders = request.user.purchase_set.filter(state = 'BT').order_by('date')
    container = ContainerFkObjects(orders,'product_id',Documents.all_objects)
    for order in orders:
        document = container.get_fk_object(order.product_id)
        order.product_title = document.title
    context['products'] = orders
    return render_to_response('user/basket.html',context,context_instance=RequestContext(request))

