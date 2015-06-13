from prospere.lib.test import ExtraTestCase, DocumentTestCase, MarketTestCase
from prospere.contrib.cabinet.forms import AddSectionForm

from prospere.contrib.cabinet.models import Documents, Sections
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from prospere.contrib.cabinet.models import Storages

from operator import attrgetter

class PageSaveProfile(DocumentTestCase):
    def test_naming_urls(self):
        url = reverse('prospere_my_profile')
        self.assertEqual(url,'/profile/')

    def test_getting_page(self):
        self.login(username='user',password='password')
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'user/profile.html') 
        from prospere.contrib.account.forms import ChangeProfile
        self.failUnless(isinstance(response.context['form'],ChangeProfile))

    def test_getting_with_anonymous(self):
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,'/login/?next=/profile/') 

