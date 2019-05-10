
import os
os.chdir("..")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ui.settings")
import django
django.setup()
from django.conf import settings
from django.contrib.auth.models import User
if len(User.objects.filter(username="admin")) < 1:
    user = User.objects.create_superuser("admin", "", "admin123")
    user.save()

