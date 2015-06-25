#!../env/bin/python
"""A simple test script for the PCE portion of OnRamp.

Usage: ./test_pce.py

This script is only intended to be run in a fresh install of the repository. It
has side-effects that could corrupt module and user data if run in a production
setting.

Prior to running this script, ensure that onramp/pce/onramp_pce_setup.py has
been called and that the server is running. Also Ensure ./test_pce_config.ini
contains the proper settings.
"""
import requests
import os
import shutil
import sys
import time
from configobj import ConfigObj
from subprocess import call
from validate import Validator

onramp_ini = ConfigObj('../../onramp_pce_config.ini',
                       configspec='../onramp_config.inispec')
onramp_ini.validate(Validator())
test_ini = ConfigObj('test_pce_config.ini',
                     configspec='test_pce_config.inispec')
test_ini.validate(Validator())

def pce_request(endpoint, **kwargs):
    params = {
        'username': test_ini['username'],
        'password': test_ini['password']
    }
    params.update(kwargs)

    url = ('http://%s:%d/%s' % (onramp_ini['server']['socket_host'],
                                onramp_ini['server']['socket_port'],
                                endpoint))

    return requests.post(url, data=params)

def init_env():
    mod_dir = '../../modules/testmodule'
    shutil.copytree('testmodule', mod_dir)
    ret_dir = os.getcwd()
    os.chdir(mod_dir)
    call(['python', 'bin/onramp_deploy.py'])
    os.chdir(ret_dir)

def cleanup_env():
    shutil.rmtree('../../modules/testmodule')

def cleanup_run(run_name):
    shutil.rmtree('../../users/%s/%s' % (test_ini['username'], run_name))

def run_tests():
    g = globals()
    for k in filter(lambda x: x.startswith('test_pce_'), g.keys()):
        result = g[k]()
        if result:
            print 'Test failure: %s' % k
            print 'Error: %s' % result
            return
    print 'All tests pass!'

def test_pce_first():
    run_name = 'testsuite'
    params= {
        'projectNum': 2,
        'projectName': run_name,
        'processors': 4
    }

    # Try prebuiltlaunch
    r = pce_request('parallellaunch/prebuiltlaunch', **params)
    if r.status_code != 200:
        cleanup_run(run_name)
        return 'prebuiltlaunch Response status not OK...'
    if r.text.strip() != 'Launched a new job with admin':
        cleanup_run(run_name)
        return 'Job did not launch...'
    
    # Let job finish
    time.sleep(5)
    
    # Check for results
    r = pce_request('parallellaunch/request')
    if r.status_code != 200:
        cleanup_run(run_name)
        return 'request Response status not OK...'

    results = r.json()

    if run_name not in results.keys():
        cleanup_run(run_name)
        return 'No results for %s...' % run_name

    expected_output = ('Testing output from testmodule.Testing output from '
                       'testmodule.Testing output from testmodule.Testing '
                       'output from testmodule.')

    if results[run_name] != expected_output:
        cleanup_run(run_name)
        return 'Unexpected output...'

    cleanup_run(run_name)
    return None

if __name__ == '__main__':
    print (__doc__)
    response = raw_input('(C)ontinue or (A)bort? ')
    if response != 'C':
        sys.exit(0)

    init_env()
    try:
        run_tests()
    finally:
        cleanup_env()
