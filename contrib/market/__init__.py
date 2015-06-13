from robokassa.signals import result_received,fail_page_visited
from prospere.contrib.market.models import Dealings
from datetime import datetime

def payment_received(sender, **kwargs):
    deal = Dealings.objects.get(id=kwargs['InvId'])

    from decimal import Decimal
    if deal.cost != Decimal(kwargs['OutSum']):
        import logging
        logger = logging.getLogger('market_log')
        logger.error('[%s] Deal sum and payd sum not equal deal_id=%s (payment_received)' % ( datetime.now(),str(deal.id) ) )
        deal.state = 'NP'
    else: 
        deal.state = 'PD' 
        deal.date = datetime.now()

    deal.save()

def payment_fail(sender,**kwargs):
    deal = Dealings.objects.filter(id=kwargs['InvId']).delete()


result_received.connect(payment_received)
fail_page_visited.connect(payment_fail)

