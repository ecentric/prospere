from django.conf.urls.defaults import patterns,include, url
from django.views.generic.simple import direct_to_template
from django.contrib.auth import views

urlpatterns = patterns('',
    url(r'^$', 'prospere.copia.views.start_page'),
    url(r'^search/$', 'prospere.copia.views.general.search_results',name = 'prospere_search'),
    url(r'^document/(?P<document_id>\d+)/$','prospere.copia.views.general.document', name='prospere_document'),
    # json_actions
    url(r'^vote/$','prospere.copia.views.json_actions.vote', name='prospere_vote'),
    url(r'^get_storage_tree/$', 'prospere.copia.views.json_actions.get_storage_tree', name='prospere_get_storage_tree'),
    # account
    url(r'^profile/$','prospere.copia.views.user.change_profile',name='prospere_my_profile'),
    url(r'^user/(?P<username>.+)/$','prospere.copia.views.general.user_page', name='prospere_user_page'),
    # market
	#url(r'^purchases/$','prospere.copia.views.user.my_purchases',name="prospere_purchases"),
    #url(r'^basket/$','prospere.copia.views.user.basket',name="prospere_basket"),
    #url(r'^sales/$', 'prospere.copia.views.user.sales', name='prospere_sales'),

    url(r'^login/$','prospere.copia.views.general.login',{'template_name':'general/login.html'}, name = 'prospere_login'),
    url(r'^logout/$',views.logout,{'next_page':'/'}, name = 'prospere_logout'),

    url(r'^pay_ways/$',direct_to_template,{'template':'general/pay_ways.html'}, name = 'prospere_pay_ways'),
)
