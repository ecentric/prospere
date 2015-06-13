from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
import views

urlpatterns = patterns('',
	url(r'^post_comment/$', views.post_comment, name="prospere_post_comment"),
	url(r'^post_comment_ajax/$', views.post_comment_ajax, name="prospere_post_comment_ajax"),
	url(r'^edit_comment_ajax/$', views.edit_comment_ajax, name="prospere_edit_comment_ajax"),
	url(r'^delete_comment_ajax/$', views.delete_comment_ajax, name="prospere_delete_comment_ajax"),
	url(r'^get_comment_tree/(?P<content_type>\d+)/(?P<object>\d+)/$', views.get_comment_tree, name="prospere_get_comment_tree")
)
