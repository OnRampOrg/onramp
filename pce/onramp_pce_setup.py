#!/usr/bin/env python
"""Configure the environment for the onramp REST server.

Usage: ./onramp_setup.py

This script sets up a virtual environment for the REST server, installs
dependencies need by the REST server, imports default educational modules into
the environment, and creates a default admin user.
"""

import json
import os
import shutil
import sys
from subprocess import call
from tempfile import mkstemp

source_dir = 'src'
env_dir = source_dir + '/env'
package_name = 'PCE'
users_dir = 'users'
modules_dir = 'modules'
log_dir = 'log'
prebuilt_dir = '../modules'
module_state_dir = 'src/state/modules'

if os.path.exists(env_dir):
    print 'Server appears to be already installed.'
    response = raw_input('(R)emove and re-install or (A)bort? ')
    if response != 'R':
        sys.exit('Aborted')
    shutil.rmtree(env_dir, True)
    shutil.rmtree(users_dir, True)
    shutil.rmtree(modules_dir, True)
    shutil.rmtree(log_dir, True)
    shutil.rmtree(module_state_dir, True)

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Set up folder structure for modules
if not os.path.exists(modules_dir):
    os.makedirs(modules_dir)
if not os.path.exists(module_state_dir):
    os.makedirs(module_state_dir)

# Setup virtual environment
call(['virtualenv', '-p', 'python2.7', env_dir])
call([env_dir + '/bin/pip', 'install', '-r', source_dir + '/requirements.txt'])

# Set pce_root in PCE packagage
cwd = os.getcwd()
pce_file = os.path.join(os.path.join(cwd, source_dir),
                        os.path.join(package_name, '__init__.py'))
fh, abs_path = mkstemp()
pce_root_found = False
with open(abs_path, 'w') as temp_file:
    with open(pce_file, 'r') as f:
        for line in f:
            if line.startswith('pce_root ='):
                pce_root_found = True
                temp_file.write("pce_root = '%s'\n" % cwd)
            else:
                temp_file.write(line)
    if not pce_root_found:
        temp_file.write("pce_root = '%s'\n" % cwd)
os.close(fh)
os.remove(pce_file)
shutil.move(abs_path, pce_file)
            
# Link PCE to virtual environment
call(['cp', '-rs', cwd + '/' + source_dir + '/' + package_name,
      env_dir + '/lib/python2.7/site-packages/' + package_name])

# Use virtual environment to complete server setup
call([env_dir + '/bin/python', source_dir + '/stage_two.py'])
