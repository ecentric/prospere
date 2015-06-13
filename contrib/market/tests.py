from django.test import TestCase
from prospere.lib.test import MarketTestCase
from models import Dealings
from prospere.contrib.cabinet.models import Documents
from datetime import datetime
from django.core.urlresolvers import reverse

class ActionAddToBasket(MarketTestCase):

    def test_naming(self):
        url = reverse('prospere_add_to_basket')
        self.assertEqual(url,'/market/add_to_basket/')

    def test_adding_that_not_in_basket(self):
        self.login(username='user',password='password')
        response = self.client.post('/market/add_to_basket/',{ 'document_id' : self.disseminator_document.pk })
        deal = Dealings.objects.get(product=self.disseminator_document.pk)
        products = Dealings.objects.filter(buyer = self.user,state="BT")
        self.assertQuerysetIdEqual(products,[self.BT_deal.pk, deal.pk])
        self.assertEqual(deal.cost, self.disseminator_document.cost)
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,'/?message=basket_product_added')

    def test_adding_that_in_basket(self):
        self.login(username='user',password='password')
        response = self.client.post('/market/add_to_basket/',{ 'document_id' : self.paid_disseminator_document_BT.pk })
        products = Dealings.objects.filter(buyer = self.user,state="BT")
        self.assertQuerysetIdEqual(products,[self.BT_deal.pk])
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,'/?message=basket_product_present')

    def test_adding_whith_out_argument(self):
        self.login(username='user',password='password')
        response = self.client.post('/market/add_to_basket/')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'error.html')

    def test_getting_page(self):
        self.login(username='user',password='password')
        response = self.client.get('/market/add_to_basket/')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'error.html')

    def test_adding_that_not_in_basket_with_anonymous(self):
        response = self.client.post('/market/add_to_basket/',{ 'document_id' : self.disseminator_document.pk })
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,'/login/')

class ActionDeleteFromBasket(MarketTestCase):
    def test_naming(self):
        url = reverse('prospere_delete_from_basket')
        self.assertEqual(url,'/market/delete_from_basket/')

    def test_deleting(self):
        self.login(username='user',password='password')
        response = self.client.post('/market/delete_from_basket/',{ 'deal_id' : self.BT_deal.pk })
        deals = Dealings.objects.filter(buyer = self.user,state="BT")
        self.assertQuerysetIdEqual(deals,[])
        self.assertRedirects(response,'/?message=basket_product_deleted')

    def test_deleting_not_own(self):
        self.login(username='user',password='password')
        response = self.client.post('/market/delete_from_basket/',{ 'deal_id' : self.disseminator_BT_deal.pk })
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'error.html')

    def test_deleting_whithout_argument(self):
        self.login(username='user',password='password')
        response = self.client.post('/market/delete_from_basket/')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'error.html')

    def test_getting_page(self):
        self.login(username='user',password='password')
        response = self.client.get('/market/delete_from_basket/')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'error.html')

    def test_deleting_with_anonymous(self):
        response = self.client.post('/market/delete_from_basket/',{ 'deal_id' : self.BT_deal.pk })
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,'/login/')

class ActionBuy(MarketTestCase):
    def test_naming(self):
        url = reverse('prospere_buy')
        self.assertEqual(url,'/market/buy/')

    def test_buy(self):
        self.login(username='user',password='password')
        response = self.client.post('/market/buy/',{ 'deal_id' : self.BT_deal.pk })
        deals = Dealings.objects.filter(buyer = self.user,state="WP")
        self.assertQuerysetIdEqual(deals,[self.BT_deal.pk,self.WP_deal.pk])

        deal = Dealings.objects.get(pk=self.BT_deal.pk)
        self.failIf(deal.product.last_purchase is None)

        self.assertEqual(response.status_code,302)
        self.failUnless('OutSum=10.30&InvId='+str(self.BT_deal.pk) in response['Location'])

    def test_buy_whithout_argument(self):
        self.login(username='user',password='password')
        response = self.client.post('/market/buy/')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'error.html')

    def test_getting_page(self):
        self.login(username='user',password='password')
        response = self.client.get('/market/buy/')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'error.html')

    def test_buy_with_anonymous(self):
        response = self.client.post('/market/buy/',{ 'deal_id' : self.BT_deal.pk })
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,'/login/')

class ActionDownloadPurchase(MarketTestCase):
    def test_naming(self):
        url = reverse('prospere_download_purchase')
        self.assertEqual(url,'/market/download_purchase/')

    def test_redirecting_to_file(self):
        self.login(username='user',password='password')
        response = self.client.post('/market/download_purchase/',{ 'deal_id' : self.PD_deal.pk })

        self.assertEqual(response.status_code,302)
        from urlparse import urlsplit
        scheme, netloc, path, query, fragment = urlsplit(response['Location'])
        self.assertEqual(path,self.PD_deal.product.get_file_url())

    def test_redirecting_to_file_that_not_exists(self):
        self.login(username='user',password='password')
        self.PD_deal.product.delete_file()
        response = self.client.post('/market/download_purchase/',{ 'deal_id' : self.PD_deal.pk })

        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,'/?message=basket_file_unavailable')

    def test_download_not_own_purchase(self):
        self.login(username='user',password='password')
        response = self.client.post('/market/download_purchase/',{ 'deal_id' : self.disseminator_PD_deal.pk })
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'error.html')

    def test_download_not_PD_purchase(self):
        self.login(username='user',password='password')
        response = self.client.post('/market/download_purchase/',{ 'deal_id' : self.WP_deal.pk })
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'error.html')

    def test_downloading_whithout_argument(self):
        self.login(username='user',password='password')
        response = self.client.post('/market/download_purchase/')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'error.html')

    def test_getting_page(self):
        self.login(username='user',password='password')
        response = self.client.get('/market/download_purchase/')
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'error.html')

    def test_buy_with_anonymous(self):
        response = self.client.post('/market/download_purchase/',{ 'deal_id' : self.PD_deal.pk })
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,'/login/')

from robokassa.signals import result_received, success_page_visited, fail_page_visited

class ActionCheckRobokassaSignals(MarketTestCase):

    def test_handler_recrive_signal(self):
        result_received.send(sender = None, InvId = self.WP_deal.pk, OutSum = self.WP_deal.cost)
        deals = Dealings.objects.filter(buyer = self.user,state="PD")
        self.assertQuerysetIdEqual(deals,[self.PD_deal.pk,self.WP_deal.pk])
        # wrong Sum
        result_received.send(sender = None, InvId = self.BT_deal.pk, OutSum = "2.50")
        deals = Dealings.objects.filter(buyer = self.user,state="PD")
        self.assertQuerysetIdEqual(deals,[self.PD_deal.pk,self.WP_deal.pk])

    def test_handler_payment_fail(self):
        fail_page_visited.send(sender = None, InvId = self.WP_deal.pk, OutSum = self.WP_deal.cost)
        deals = Dealings.objects.filter(buyer = self.user,state="PD")
        self.assertQuerysetIdEqual(deals,[self.PD_deal.pk])
        deals = Dealings.objects.filter(buyer = self.user,state="WP")
        self.assertQuerysetIdEqual(deals,[])
        

