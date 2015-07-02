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


class _JSONResourceTest(unittest.TestCase):
    """Encapsulate functionality/attrs common to all JSON response testing.

    Methods:
        check_base_JSON_attrs: Check attrs that should be consistent accross all
            API JSON responses.
    """
    def check_base_JSON_attrs(self, obj):
        """Check attrs that should be consistent accross all API JSON responses.

        Args:
            obj (dict): Response object to check.
        """
        self.assertIn('status_code', obj.keys())
        self.assertIn('status_msg', obj.keys())
        self.assertIn('url', obj.keys())
        self.assertIn('api_root', obj.keys())
        self.assertTrue(obj['api_root'].endswith('/api/'))


class ModulesEndpointTest(_JSONResourceTest):
    """Test the API for PCE educational modules.

    Class attrs:
        modules_dir (str): Relative path to deployed modules base dir.
        testmodule_dir (str): Relative path to deployed testing module dir.
    
    Methods:
        test_GET_on_list: Test resource response to various GET requests.
        test_GET_on_specific: Test resource response to various GET requests on
            individual items.
        check_module: Check traits common to all dict reps of PCE educational
            modules.
    """
    modules_dir = '../../modules'
    testmodule_dir = modules_dir + '/testmodule'

    def setUp(self):
        """Setup the testing environment for modules testing."""
        shutil.copytree('testmodule', self.testmodule_dir)
        ret_dir = os.getcwd()
        os.chdir(self.testmodule_dir)
        call(['python', 'bin/onramp_deploy.py'])
        os.chdir(ret_dir)
    
    def tearDown(self):
        """Cleanup the testing environment from modules testing."""
        if(os.path.isdir(self.testmodule_dir)):
            shutil.rmtree(self.testmodule_dir)

    def test_GET_on_list(self):
        """Test resource response to various GET requests on the list of items.
        """
        # Request under normal conditions:
        r = pce_get('modules/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        print d
        self.check_base_JSON_attrs(d)
        self.assertEqual(d['status_code'], 0)
        self.assertEqual(d['status_msg'], 'Success')
        self.assertTrue(d['url'].endswith('/modules/'))
        self.assertIn('modules', d.keys())
        self.assertNotIn('module', d.keys())
        self.assertTrue(d['modules'])
        for k in d['modules']:
            self.check_module(d['modules'][k])
        self.assertIn('testmodule', d['modules'].keys())

        # Check to make sure no exceptions and proper response when no modules
        # found:
        shutil.rmtree(self.modules_dir)
        os.mkdir(self.modules_dir)
        r = pce_get('modules/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_base_JSON_attrs(d)
        self.assertEqual(d['status_code'], 0)
        self.assertEqual(d['status_msg'], 'Success')
        self.assertTrue(d['url'].endswith('/modules/'))
        self.assertIn('modules', d.keys())
        self.assertNotIn('module', d.keys())
        self.assertFalse(d['modules'])

        # Check proper status code and message given when modules dir missing:
        shutil.rmtree(self.modules_dir)
        r = pce_get('modules/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_base_JSON_attrs(d)
        self.assertEqual(d['status_code'], -1)
        self.assertEqual(d['status_msg'], 'Modules root folder does not exist')
        self.assertTrue(d['url'].endswith('/modules/'))
        self.assertNotIn('modules', d.keys())
        self.assertNotIn('module', d.keys())

    def test_GET_on_specific(self):
        """Test resource response to various GET requests on individual items.
        """
        # Request under normal conditions:
        r = pce_get('modules/testmodule/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_base_JSON_attrs(d)
        self.assertEqual(d['status_code'], 0)
        self.assertEqual(d['status_msg'], 'Success')
        self.assertTrue(d['url'].endswith('/modules/testmodule/'))
        self.assertIn('module', d.keys())
        self.assertNotIn('modules', d.keys())
        self.check_module(d['module'])

        # Check to make sure no exceptions and proper response when module not
        # found:
        shutil.rmtree(self.modules_dir)
        os.mkdir(self.modules_dir)
        r = pce_get('modules/testmodule/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_base_JSON_attrs(d)
        self.assertEqual(d['status_code'], -2)
        self.assertEqual(d['status_msg'], 'Module testmodule does not exist')
        self.assertIsNone(d['url'])
        self.assertNotIn('module', d.keys())
        self.assertNotIn('modules', d.keys())

        # Check proper status code and message given when modules dir missing:
        shutil.rmtree(self.modules_dir)
        r = pce_get('modules/testmodule/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_base_JSON_attrs(d)
        self.assertEqual(d['status_code'], -1)
        self.assertEqual(d['status_msg'], 'Modules root folder does not exist')
        self.assertTrue(d['url'].endswith('/modules/'))
        self.assertNotIn('modules', d.keys())
        self.assertNotIn('module', d.keys())

    def check_module(self, mod):
        """Check traits common to all dict reps of PCE educational modules.

        Args:
            mod (dict): Rep of PCE educational module to check.
        """
        self.assertIn('url', mod.keys())
        s = mod['url'].split('/')[1]
        self.assertEqual(s, 'modules')
        self.assertNotEqual(mod['url'], '/modules/')


if __name__ == '__main__':
    setup()
    unittest.main()
    teardown()
