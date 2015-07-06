"""Complete actions needed for onramp REST server setup that require the newly
configured virtual environment.

This script is intended to be called solely by ../onramp_setup.py.
"""

import os
import shutil
from subprocess import call

from PCE.tools import create_admin

users_dir = 'users'
make_new_users = True

if os.path.exists(users_dir):
    msg = 'It appears users already exist on this system.\n'
    msg += '(R)emove current users and create new admin user or '
    msg += '(K)eep current users? '
    response = raw_input(msg)
    if response != 'R':
        make_new_users = False
    else:
        shutil.rmtree(users_dir)

if make_new_users:
    os.makedirs(users_dir)
    create_admin(users_dir)
