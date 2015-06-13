from django.conf.urls.defaults import patterns, url
import views

urlpatterns = patterns('',
    url(r'^get_notifications/$', views.get_notifications, name='prospere_get_notifications'),
    url(r'^delete/$', views.delete_notification, name='prospere_delete_notification'),
)

