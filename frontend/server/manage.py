#!/usr/bin/env python

import os
import sys
import site

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('../virtual-env')

# Add the app's directory to the PYTHONPATH
cwd = os.getcwd()
sys.path.append(cwd)
sys.path.append(cwd.rstrip("/ui"))
sys.path.append("{}/virtual-env/lib/python2.7/site-packages".format(cwd.rstrip("/ui")))

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ui.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django
            django.setup()
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise
    execute_from_command_line(sys.argv)
