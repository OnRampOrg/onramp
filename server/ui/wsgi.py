"""
WSGI config for frontend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

sys.path.append("/OnRamp")
sys.path.append("/OnRamp/ui")
sys.path.append("/OnRamp/virtual-env/lib/python2.7/site-packages")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ui.settings")

application = get_wsgi_application()
