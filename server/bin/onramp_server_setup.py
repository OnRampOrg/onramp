#!/usr/bin/env python
"""Configure the environment for the OnRamp REST server.

Usage: ./bin/onramp_server_setup.py

This script sets up a virtual environment for the REST server, installs
dependencies need by the REST server, imports default educational modules into
the environment, and creates a default admin user.
"""

import os
import shutil
import sys
from subprocess import call


package_name = 'Server'
source_dir = 'src'
env_dir = source_dir + '/env'
tmp_users_dir = 'users'
tmp_pce_dir = 'pce'
log_dir = 'log'


#
# Check if we have already done this
#
if os.path.exists(env_dir):
    print 'Server appears to be already installed.'
    response = raw_input('(R)emove and re-install or (A)bort? ')
    if response != 'R':
        sys.exit('Aborted')
    shutil.rmtree(env_dir)
    shutil.rmtree(log_dir, True)
    shutil.rmtree(tmp_users_dir, True)
    shutil.rmtree(tmp_pce_dir, True)

#
# Create the log directory
#
if not os.path.exists(log_dir):
    os.makedirs(log_dir)


#
# Create the base temporary directories
#
if not os.path.exists(tmp_users_dir):
    os.makedirs(tmp_users_dir)
if not os.path.exists(tmp_pce_dir):
    os.makedirs(tmp_pce_dir)


#
# Setup virtual environment
#
call(['virtualenv', '-p', 'python2.7', env_dir])
call([env_dir + '/bin/pip', 'install', '-r', source_dir + '/requirements.txt'])

# Link Server to virtual environment
# FIXME: This assumes python2.7. Need to find a way with virtualenv/pip to
# enforce this.
cwd = os.getcwd()
call(['cp', '-rs', cwd + '/' + source_dir + '/' + package_name,
      env_dir + '/lib/python2.7/site-packages/' + package_name])

# Use virtual environment to complete server setup
call([env_dir + '/bin/python', source_dir + '/stage_two.py'])
