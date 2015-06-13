"""
A management command which deletes expired bans and handle new

"""

from django.core.management.base import BaseCommand, NoArgsCommand
from django.contrib.sites.models import Site
from django.conf import settings


class Command(NoArgsCommand):
    help = 'change site name and domain'

    def handle_noargs(self, **options):
        Site.objects.filter(id = settings.SITE_ID).update(name = "copia.org.ua",domain = "copia.org.ua")

