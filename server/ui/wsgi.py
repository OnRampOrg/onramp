"""
WSGI config for frontend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os
import sys
import site

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('/home/drewguillien/onramp/server/virtual-env')

# Add the app's directory to the PYTHONPATH
# used to be relative, now hard coding...  SSF - 10/27/17
sys.path.append("/home/drewguillien/onramp/server")
sys.path.append('/home/drewguillien/onramp/server/ui')
sys.path.append("/home/drewguillien/onramp/server/virtual-env/lib/python2.7/site-packages")

# to set environment settings for Django apps
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ui.settings")

# # Activate your virtual env
# activate_env = os.path.expanduser('../virtual-env/bin/activate_this.py')
# execfile(activate_env, dict(__file__=activate_env))

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
