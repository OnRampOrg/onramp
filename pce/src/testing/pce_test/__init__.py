"""Unit testing and testing environment setup for OnRamp PCE.

Exports:
    setup: Setup the testing environment.
    teardown: Cleanup the testing environment.
    pce_url: Build the full URL for the resource at a specified endpoint.
    pce_post: Execute a POST request to a given endpoint with given params.
    pce_get: Execute a GET request to a given endpoint with given params.
    ModuleEndpointTest: Unit tests for the PCE modules resource.
"""
import json
import requests
import os
import shutil
import sys
import time
import unittest
from configobj import ConfigObj
from subprocess import call
from validate import Validator

def setup():
    """Setup the testing environment."""
    global onramp_ini
    global test_ini

    onramp_ini = ConfigObj('../../onramp_pce_config.ini',
                           configspec='../onramp_config.inispec')
    onramp_ini.validate(Validator())
    test_ini = ConfigObj('test_pce_config.ini',
                         configspec='test_pce_config.inispec')
    test_ini.validate(Validator())

    mod_dir = '../../modules/testmodule'
    shutil.copytree('testmodule', mod_dir)
    ret_dir = os.getcwd()
    os.chdir(mod_dir)
    call(['python', 'bin/onramp_deploy.py'])
    os.chdir(ret_dir)

def teardown():
    """Cleanup the testing environment."""
    testmodule_dir = '../../modules/testmodule'
    if(os.path.isdir(testmodule_dir)):
        shutil.rmtree(testmodule_dir)

def pce_url(endpoint):
    """Build the full URL for the resource at the specified endpoint.

    Args:
        enpoint (str): Endpoint of the resource reqested.
    """
    return ('http://%s:%d/%s' % (onramp_ini['server']['socket_host'],
                                 onramp_ini['server']['socket_port'],
                                 endpoint))

def pce_post(endpoint, **kwargs):
    """Execute a POST to the specified endpoint.

    Args:
        enpoint (str): Endpoint of the resource reqested.

    Kwargs: HTML formfield key/value pairs to use for the request.
    """
    fields = {
        'username': test_ini['username'],
        'password': test_ini['password']
    }
    fields.update(kwargs)
    return requests.post(pce_url(endpoint), data=fields)

def pce_get(endpoint, **kwargs):
    """Execute a GET to the specified endpoint.

    Args:
        enpoint (str): Endpoint of the resource reqested.

    Kwargs: HTML query params key/value pairs to use for the request.
    """
    return requests.get(pce_url(endpoint), params=kwargs)


class ModulesEndpointTest(unittest.TestCase):
    """Test the API for PCE educational modules.
    
    Methods:
        test_GET: Test resource response to various GET requests.
    """
    def test_GET(self):
        """Test resource response to various GET requests."""
        modules_dir = '../../modules'

        # Request under normal conditions:
        r = pce_get('modules/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.assertEqual(d['status_code'], 0)
        self.assertEqual(d['status_msg'], 'Success')
        self.assertTrue(d['url'].endswith('/modules/'))
        self.assertTrue(d['api_root'].endswith('/api/'))
        self.assertIn('modules', d.keys())
        self.assertTrue(d['modules'])
        self.assertIn('testmodule', d['modules'].keys())

        # Check to make sure no exceptions and proper response when no modules
        # found:
        shutil.rmtree(modules_dir)
        os.mkdir(modules_dir)
        r = pce_get('modules/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.assertEqual(d['status_code'], 0)
        self.assertEqual(d['status_msg'], 'Success')
        self.assertTrue(d['url'].endswith('/modules/'))
        self.assertTrue(d['api_root'].endswith('/api/'))
        self.assertIn('modules', d.keys())
        self.assertFalse(d['modules'])

        # Check proper status code and message given when modules dir missing:
        shutil.rmtree(modules_dir)
        r = pce_get('modules/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.assertEqual(d['status_code'], -1)
        self.assertEqual(d['status_msg'], 'Modules root folder does not exist')
        self.assertTrue(d['url'].endswith('/modules/'))
        self.assertTrue(d['api_root'].endswith('/api/'))
        self.assertNotIn('modules', d.keys())


#class PrebuiltLaunchTest(unittest.TestCase):
#    def setUp(self):
#        LIMIT = 100
#        i = 0
#        prefix = 'test_run'
#        str_args = (test_ini['username'], prefix, i)
#
#        # This is because the server may not take kindly to rapid recreation of
#        # folders that have been recently deleted. NFS propogation issues, etc.
#        while (os.path.isdir('../../../users/%s/%s%d' % str_args) \
#               and i < LIMIT):
#            i += 1
#        self.assertLess(i, LIMIT)
#
#        self.run_name = 'test_run%d' % i
#
#    def tearDown(self):
#        #shutil.rmtree('../../users/%s/%s' % (test_ini['username'],
#                      #self.run_name))
#        pass
#
#    def test_valid_request(self):
#        params= {
#            'projectNum': 2,
#            'projectName': self.run_name,
#            'processors': 4
#        }
#    
#        # Try prebuiltlaunch
#        r = pce_request('parallellaunch/prebuiltlaunch', **params)
#        self.assertEqual(r.status_code, 200)
#        self.assertEqual(r.text.strip(), 'Launched a new job with admin')
#        
#        # Let job finish
#        time.sleep(5)
#        
#        # Check for results
#        r = pce_request('parallellaunch/request')
#        self.assertEqual(r.status_code, 200)
#        results = r.json()
#        self.assertIn(self.run_name, results.keys())
#    
#        expected_output = ('Testing output from testmodule.Testing output from '
#                           'testmodule.Testing output from testmodule.Testing '
#                           'output from testmodule.')
#    
#        self.assertEqual(results[self.run_name], expected_output)
#
#    def test_valid_request_num_tasks(self):
#        params= {
#            'projectNum': 2,
#            'projectName': self.run_name,
#            'processors': 3
#        }
#    
#        # Try prebuiltlaunch
#        r = pce_request('parallellaunch/prebuiltlaunch', **params)
#        self.assertEqual(r.status_code, 200)
#        self.assertEqual(r.text.strip(), 'Launched a new job with admin')
#        
#        # Let job finish
#        time.sleep(5)
#        
#        # Check for results
#        r = pce_request('parallellaunch/request')
#        self.assertEqual(r.status_code, 200)
#        results = r.json()
#        self.assertIn(self.run_name, results.keys())
#    
#        expected_output = ('Testing output from testmodule.Testing output from '
#                           'testmodule.Testing output from testmodule.')
#    
#        self.assertEqual(results[self.run_name], expected_output)

if __name__ == '__main__':
    setup()
    unittest.main()
    teardown()
