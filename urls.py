from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import direct_to_template
from django.contrib.auth import views
from settings import MEDIA_ROOT
#from prospere.copia.views import start_page
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    #Main page and admin
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('prospere.copia.urls')),
    #include apps urls
    url(r'^comments/', include('prospere.contrib.comment.urls')),
    url(r'^notification/', include('prospere.contrib.notification.urls')),
    url(r'^account/', include('prospere.contrib.account.urls')),
    #url(r'^market/', include('prospere.contrib.market.urls')),
    url(r'^cabinet/', include('prospere.contrib.cabinet.urls')),
    url(r'^tinymce/', include('tinymce.urls')),

    url(r'^error/', direct_to_template, { 'template' : 'error.html'} ),

    #Not prodaction!!!!!
    #url(r'^media/files/(?P<path>.*)$', 'django.views.static.serve', {'document_root': MEDIA_ROOT}),
)
