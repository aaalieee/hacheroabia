import os
import sys

#path where you can find the mange.py

path = '/home/superjubnick/FireApp/boilerplate/projecsite'
if path not in sys.path:
    sys.path.insert(0, path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projectsite.settings")
from django.core.wsgi import get_wsgi_application
from django.contrib.staticfiles.handlers import StaticFilesHandler
application = StaticFilesHandler(get_wsgi_application())