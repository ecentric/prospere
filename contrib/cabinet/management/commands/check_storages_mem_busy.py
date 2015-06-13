'''
This command check and correct storage mem_busy failure
'''

from django.core.management.base import BaseCommand, NoArgsCommand, CommandError
from prospere.contrib.cabinet.models import Documents, Storages
from django.db.models import Sum

class Command(NoArgsCommand):
    help = 'recalc storages mem_busy'
    
    def print_error(self, s):
        if hasattr(self, 'stderr'):
            self.stderr.write(s)

    def handle_noargs(self, **options):
        storages = Storages.objects.all()
        for storage in storages:
            mem_busy = Documents.objects.filter(storage = storage).aggregate(busy = Sum('file_size'))['busy']
            if mem_busy is None: mem_busy = 0
            if storage.mem_busy != mem_busy:
                self.print_error("Storage mem_busy failure: id = " + str(storage.id))
                storage.mem_busy = mem_busy
                storage.save()
                self.print_error(" - fixed\n")

