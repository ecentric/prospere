from django.conf.urls.defaults import patterns,include, url
from django.views.generic.simple import direct_to_template
import views.section as section
import views.document as document

urlpatterns = patterns('',
    #cabinet urls

    url(r'^add_document/(?P<section>\d+)/$', document.add_document, name='prospere_add_document'),
    url(r'^edit_document/(?P<document_id>\d+)/$', document.edit_document, name='prospere_edit_document'),
    url(r'^change_document_access/$', document.change_document_access, name='prospere_change_document_access'),
    url(r'^delete_document/$', document.delete_document, name = 'prospere_delete_document'),

    # WARNING : Everyone can vote few times
    #url(r'^vote_document/$', 'prospere.contrib.cabinet.views.document.vote_document',name = 'prospere_vote_document'),

    url(r'^add_section/$', section.add_section, name='prospere_add_section'),
    url(r'^edit_section/$', section.edit_section, name='prospere_edit_section'),
    url(r'^change_section_access/$', section.change_section_access, name='prospere_change_section_access'),
    url(r'^delete_section/$', section.delete_section, name = 'prospere_delete_section'),
)

