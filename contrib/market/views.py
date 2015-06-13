#coding: utf-8
from django.shortcuts import render_to_response,redirect
from django.views.generic.simple import direct_to_template
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from prospere.contrib.market.models import Dealings
from robokassa.forms import RobokassaForm
from prospere.contrib.cabinet.models import Documents

@login_required(redirect_field_name=None)
def buy(request):

    if request.method == 'POST':
        from robokassa.forms import RobokassaForm
        from datetime import datetime

        deal_id = request.POST.get('deal_id',False)
        if not deal_id: return direct_to_template(request,'error.html')
            
        deal = Dealings.objects.get(pk = deal_id)
        deal.state = "WP"
        deal.product.last_purchase = datetime.now()
        deal.product.save()
        deal.save()

        form = RobokassaForm(initial={
                   'OutSum': str(deal.cost),
                   'InvId': deal.id,
                   'Desc': '',
                   'Email': request.user.email,
                   # 'IncCurrLabel': '',
                   'Culture': 'ru',
               })
        return redirect(form.get_redirect_url())

    return direct_to_template(request,'error.html')

@login_required(redirect_field_name=None)
def download_purchase(request):

    if request.method == 'POST':
        deal_id = request.POST.get('deal_id',False)
        if not deal_id: return direct_to_template(request,'error.html')

        deal = Dealings.objects.get(pk = deal_id)
        if deal.buyer != request.user or deal.state != 'PD': return direct_to_template(request,'error.html')

        url = deal.product.get_file_url()
        if url is None: 
            from prospere.lib import set_get_argument
            redirect_to = request.POST.get('next', '/')
            redirect_to = set_get_argument(redirect_to,"message","basket_file_unavailable")
            return redirect(redirect_to)

        return redirect(url)

    return direct_to_template(request,'error.html')

@login_required(redirect_field_name=None)
def add_to_basket(request):

    if request.method == 'POST':
        from datetime import datetime

        document_id = request.POST.get('document_id',False)
        if not document_id: return direct_to_template(request,'error.html')

        redirect_to = request.POST.get('next', '/')

        from prospere.lib import set_get_argument
        count = Dealings.objects.filter(product = document_id, buyer=request.user).count()
        if count == 0:
            document = Documents.objects.get(pk = document_id)
            dial = Dealings.objects.create(buyer = request.user, seller = document.user, product = document,
                                       cost = document.cost, date = datetime.now(), state = "BT")
            redirect_to = set_get_argument(redirect_to,"message","basket_product_added")
        else: redirect_to = set_get_argument(redirect_to,"message","basket_product_present")

        return redirect(redirect_to)

    return direct_to_template(request,'error.html')

@login_required(redirect_field_name=None)
def delete_from_basket(request):

    if request.method == 'POST':
        from datetime import datetime

        deal_id = request.POST.get('deal_id',False)
        if not deal_id: return direct_to_template(request,'error.html')

        redirect_to = request.POST.get('next', '/')

        from prospere.lib import set_get_argument
        deal = Dealings.objects.get(pk = deal_id)
        if deal.buyer != request.user or deal.state != 'BT': return direct_to_template(request,'error.html')
        deal.delete()

        redirect_to = set_get_argument(redirect_to,"message","basket_product_deleted")

        return redirect(redirect_to)

    return direct_to_template(request,'error.html')

