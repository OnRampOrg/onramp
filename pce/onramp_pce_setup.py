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
prebuilt_dir = '../modules'

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

# Deploy modules shipped with onramp
if not os.path.exists(modules_dir):
    os.makedirs(modules_dir)

ret_dir = os.getcwd()
for name in os.listdir(prebuilt_dir):
    next_path = os.path.join(prebuilt_dir, name)
    if os.path.isdir(os.path.join(prebuilt_dir, name)):
        if name != 'template':
            new_path = os.path.join(modules_dir, name)
            if not os.path.exists(new_path):
                shutil.copytree(next_path, new_path)
                os.chdir(new_path)
                # Assuming that modules shipped with onramp will not have
                # onramp_deploy.py return 1:
                call(['python', 'bin/onramp_deploy.py'])
                os.chdir(ret_dir)

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
