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

    tmpl_conf  = "bin/onramp_pce_config.ini.tmpl"
    final_conf = "bin/onramp_pce_config.ini"
    
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
    if os.path.exists(final_conf) is True:
        print "=" * 70
        print 'Warning: PCE Service configuration file present.'
        print "=" * 70

        response = raw_input('(R)eplace or (K)eep? ')
        if response == 'R' or response == 'r':
            call(['rm', final_conf])
            call(['cp', tmpl_conf, final_conf])
    else:
        call(['cp', tmpl_conf, final_conf])
    call(['chmod', 'og+rX', final_conf])

    print "==>"
    print "==> NOTICE: Please edit the file: " + final_conf
    print "==>"


    ###################################################
    print "=" * 70
    print "Status: Setup the virtual environment"
    print "        This may take a while..."
    print "=" * 70

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


    ###################################################
    print "=" * 70
    print "Status: Setup Complete"
    print "=" * 70
