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


if __name__ == '__main__':
    setup()
    unittest.main()
    teardown()
