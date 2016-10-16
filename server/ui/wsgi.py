"""
WSGI config for frontend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os
import sys

base_dir = "/".join(os.getcwd().split("/")[0:-1])
sys.path.append(base_dir)
sys.path.append("{}/virtual-env/lib/python2.7/site-packages".format(base_dir))

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

application = get_wsgi_application()
