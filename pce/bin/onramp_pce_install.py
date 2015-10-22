#!/usr/bin/env python
"""Configure the environment for the onramp REST server.

Usage: bin/onramp_pce_install.py

This script sets up a virtual environment for the REST server, installs
dependencies need by the REST server, imports default educational modules into
the environment, and creates a default admin user.
"""

import json
import os
import shutil
import sys
import time
from subprocess import call
from tempfile import mkstemp

if __name__ == '__main__':
    source_dir = 'src'
    env_dir = source_dir + '/env'
    package_name = 'PCE'
    users_dir = 'users'
    modules_dir = 'modules'
    log_dir = 'log'
    prebuilt_dir = '../modules'
    module_state_dir = 'src/state/modules'
    job_state_dir = 'src/state/jobs'

    tmpl_conf  = "bin/onramp_pce_config.cfg.tmpl"
    final_conf = "bin/onramp_pce_config.cfg"
    
    # If the PCE service is already deployed/installed
    if os.path.exists(env_dir):
        print "=" * 70
        print 'Warning: PCE Service appears to be already installed.'
        print "=" * 70

        response = raw_input('(R)emove and re-install or (A)bort? ')
        if response != 'R' and response != 'r':
            sys.exit('Aborted')
        shutil.rmtree(env_dir, True)
        shutil.rmtree(users_dir, True)
        shutil.rmtree(modules_dir, True)
        shutil.rmtree(log_dir, True)
        shutil.rmtree(module_state_dir, True)
        shutil.rmtree(job_state_dir, True)
    
    # Create the log directory
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Set up folder structure for modules
    if not os.path.exists(modules_dir):
        os.makedirs(modules_dir)
    if not os.path.exists(module_state_dir):
        os.makedirs(module_state_dir)
    if not os.path.exists(job_state_dir):
        os.makedirs(job_state_dir)

    
    #
    # Setup the configuration file(s)
    #
    show_edit_msg = False
    if os.path.exists(final_conf) is True:
        print "=" * 70
        print 'Warning: PCE Service configuration file present.'
        print "=" * 70

        response = raw_input('(R)eplace or (K)eep? ')
        if response == 'R' or response == 'r':
            call(['rm', final_conf])
            call(['cp', tmpl_conf, final_conf])
            show_edit_msg = True
    else:
        call(['cp', tmpl_conf, final_conf])
        show_edit_msg = True
    call(['chmod', 'og+rX', final_conf])



    ###################################################
    print "=" * 70
    print "Status: Setup the virtual environment"
    print "        This may take a while..."
    print "=" * 70

    # Setup virtual environment
    call(['virtualenv', '-p', 'python2.7', env_dir])
    call([env_dir + '/bin/pip', 'install', '-r', source_dir + '/requirements.txt'])
    
    # Link PCE to virtual environment
    cwd = os.getcwd()
    call(['cp', '-rs', cwd + '/' + source_dir + '/' + package_name,
          env_dir + '/lib/python2.7/site-packages/' + package_name])

    # Create PCEHelper module in virtual environment
    mod_dir = os.path.join(env_dir, 'lib', 'python2.7', 'site-packages',
                            'PCEHelper')
    mod_file = os.path.join(mod_dir, '__init__.py')
    os.mkdir(mod_dir)
    with open(mod_file, 'w') as f:
        print>>f, "pce_root = '%s'\n" % cwd

    # Use virtual environment to complete server setup
    call([env_dir + '/bin/python', source_dir + '/stage_two.py'])

    ###################################################
    print "=" * 70
    print "Status: Setup Complete"
    print "=" * 70

    if show_edit_msg:
        print "==>"
        print "==> NOTICE: Please edit the file: " + final_conf
        print "==>"
