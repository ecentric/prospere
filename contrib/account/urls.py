"""

"""
from django.conf.urls.defaults import patterns,include, url

from registration.views import activate
from registration.views import register
from django.contrib.auth import views
from prospere.contrib.account.forms import RegistrationFormUniqueEmail

urlpatterns = patterns('',
                       # Activation keys get matched by \w+ instead of the more specific
                       # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
                       # that way it can return a sensible "invalid key" message instead of a
                       # confusing 404.
                       url(r'^activate/(?P<activation_key>\w+)/$',
                           activate,
                           { 'backend': 'registration.backends.default.DefaultBackend',
                             'success_url' : '/?message=account_activate_complete',
                             'template_name': 'error.html',
                             'extra_context': {'message':'Произошла ошибка при активации'}},
                           name='registration_activate'),
                       url(r'^register/$',
                           register,
                           { 'backend': 'registration.backends.default.DefaultBackend',
                           	 'template_name': 'registration.html',
                           	 'form_class': RegistrationFormUniqueEmail, 
                             'disallowed_url' : '/?message=account_registry_closed',
                             'success_url' : '/?message=account_registration_complete', },
                           name='registration_register'),

                       # Change password by email
                       url(r'^password/reset/$', 
                                                views.password_reset, 
                                                {'template_name':'password/reset.html',
                                                 'post_reset_redirect':'/?message=account_email_sended',},
                                                 #'email_template_name':'registration/password_reset_email.txt'},
                                                name = 'prospere_password_reset'),
                       url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
                                                views.password_reset_confirm,
                                                {'template_name':'password/reset_confirm.html',
                                                 'post_reset_redirect':'/?message=account_password_changed'},),
                       # change password
                       url(r'^password/change/$', views.password_change, {'template_name':'password/change.html', 
                                                'post_change_redirect' : '/?message=account_password_changed'},
                                                name = 'prospere_password_change'),
                       # change profile
                       url(r'^save_profile/$','prospere.contrib.account.views.save_profile',name="prospere_save_profile"),
                       #url(r'^upload/progress/$', 'prospere.contrib.account.views.upload_progress', name='upload_progress'),
                       url(r'^get_bookmarks/$', 'prospere.contrib.account.views.get_bookmarks', name='prospere_get_bookmarks'),
                       url(r'^add_bookmark/$','prospere.contrib.account.views.add_bookmark',name="prospere_add_bookmark"),
                       url(r'^delete_bookmark/$','prospere.contrib.account.views.delete_bookmark',
                                                                                            name="prospere_delete_bookmark"),

                       url(r'^check_username/$','prospere.contrib.account.views.check_username',name="prospere_check_username"),
)
