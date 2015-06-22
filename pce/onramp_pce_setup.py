#!/usr/bin/env python
"""Configure the environment for the onramp REST server.

Usage: ./onramp_setup.py

This script sets up a virtual environment for the REST server, installs
dependencies need by the REST server, imports default educational modules into
the environment, and creates a default admin user.
"""

import os
import shutil
import sys
from subprocess import call

source_dir = 'src'
env_dir = source_dir + '/env'
package_name = 'PCE'
users_dir = 'users'
modules_dir = 'modules'
log_dir = 'log'
prebuilt_dir = '../PrebuiltProjects'

if os.path.exists(env_dir):
    print 'Server appears to be already installed.'
    response = raw_input('(R)emove and re-install or (A)bort? ')
    if response != 'R':
        sys.exit('Aborted')
    shutil.rmtree(env_dir)
    shutil.rmtree(users_dir, True)
    shutil.rmtree(modules_dir, True)
    shutil.rmtree(log_dir, True)

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# FIXME: This section will need to change when module deployment is understood
if not os.path.exists(modules_dir):
    os.makedirs(modules_dir)

for root, dirs, files in os.walk(prebuilt_dir):
    for name in dirs:
        if not os.path.exists(modules_dir + '/' + name):
            shutil.copytree(prebuilt_dir + '/' + name, modules_dir + '/' + name)
##############################################################################

# Setup virtual environment
call(['virtualenv', env_dir])
call([env_dir + '/bin/pip', 'install', '-r', source_dir + '/requirements.txt'])

# Link PCE to virtual environment
# FIXME: This assumes python2.7. Need to find a way with virtualenv/pip to
# enforce this.
cwd = os.getcwd()
call(['cp', '-rs', cwd + '/' + source_dir + '/' + package_name,
      env_dir + '/lib/python2.7/site-packages/' + package_name])

# Use virtual environment to complete server setup
call([env_dir + '/bin/python', source_dir + '/stage_two.py'])
