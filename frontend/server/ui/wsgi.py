"""
WSGI config for frontend project.
 
It exposes the WSGI callable as a module-level variable named ``application``.
 
For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""
 
import os

# to set environment settings for Django apps
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ui.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

