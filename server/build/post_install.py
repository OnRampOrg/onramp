import os

from django.db import IntegrityError

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ui.settings")
import subprocess
import django
django.setup()

from django.contrib.auth.models import User


def run_migrations():
    print "Running django migrations"
    os.chdir("../ui")
    # we want this to raise an error if it fails because it
    # needs to happen before anything else
    subprocess.check_call(['python', 'manage.py', 'migrate'])



def create_admin_user():
    try:
        User.objects.create_superuser("admin", "", "admin123")
        print "Admin user created!\n\tusername: admin\n\tpassword: admin123"
    except IntegrityError:
        print "Admin user with username admin already exists."


if __name__ == '__main__':
    # TODO I was unable to get this to work from the current directory
    # TODO this is because of something in my environment, so that needs to be worked out
    run_migrations()
    create_admin_user()