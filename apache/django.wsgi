import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'prospere.settings'
sys.path.insert(0, '/www')
sys.path.insert(0, '/lib/python2.6/site-packages')

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
