from django.conf.urls.defaults import patterns,include, url

urlpatterns = patterns('',
    url(r'^buy/$','prospere.contrib.market.views.buy',name="prospere_buy"),
    url(r'^download_purchase/$','prospere.contrib.market.views.download_purchase',name="prospere_download_purchase"),

    url(r'^add_to_basket/$','prospere.contrib.market.views.add_to_basket',name="prospere_add_to_basket"),
    url(r'^delete_from_basket/$','prospere.contrib.market.views.delete_from_basket',name="prospere_delete_from_basket"),

    url(r'^robokassa/', include('robokassa.urls')),
)

