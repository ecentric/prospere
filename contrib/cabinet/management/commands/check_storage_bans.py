"""
A management command which deletes expired bans and handle new

"""

from django.core.management.base import BaseCommand, NoArgsCommand

from prospere.contrib.cabinet.models import StorageBans, Storages
from datetime import datetime, timedelta
from prospere.lib import ContainerFkObjects
from prospere.copia.models import SessionBonds

class Command(NoArgsCommand):
    help = 'handle bans'

    BAN_DAYS = 5

    def handle_noargs(self, **options):

        storsge_id_list = set()
        '''
        delete old bans
        '''
        expiration_date = timedelta(days=self.BAN_DAYS)
        expired_bans = StorageBans.objects.filter(is_processed = True, creation_date__lt = datetime.now() - expiration_date)

        storage_cntr = ContainerFkObjects(expired_bans, 'storage_id', Storages.objects)
        for ban in expired_bans:
            storage = storage_cntr.get_fk_object(ban.storage_id)
            storage.mem_limit = ban.amount_of_ban + storage.mem_limit
            storage.save()
            
        expired_bans.delete()

