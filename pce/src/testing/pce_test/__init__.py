"""Unit testing and testing environment setup for OnRamp PCE.

Exports:
    setup: Setup the testing environment.
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
    return requests.post(pce_url(endpoint), data=json.dumps(kwargs),
                         headers={'content-type': 'application/json'})

def pce_get(endpoint, **kwargs):
    """Execute a GET to the specified endpoint.

    Args:
        enpoint (str): Endpoint of the resource reqested.

    Kwargs: HTML query params key/value pairs to use for the request.
    """
    return requests.get(pce_url(endpoint), params=kwargs)


class _JSONResourceTest(unittest.TestCase):
    """Encapsulate functionality/attrs common to all JSON response testing.

    Class Attrs:
        base_response_fields (list): Set of all fields that should be present in
            every response in all tests conducted by a _JSONResourceTest subclass.

    Methods:
        check_base_JSON_attrs: Check attrs that should be consistent accross all
            API JSON responses.
    """
    base_response_fields = ['status_code', 'status_msg', 'url', 'api_root']

    def check_base_JSON_attrs(self, obj):
        """Check attrs that should be consistent accross all API JSON responses.

        Args:
            obj (dict): Response object to check.
        """
        keys = obj.keys()
        for field in self.base_response_fields:
            self.assertIn(field, keys)

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
        self.assertEqual(r.status_code, 500)
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
        self.assertEqual(r.status_code, 404)
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
        self.assertEqual(r.status_code, 500)
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


class JobsEndpointTest(_JSONResourceTest):
    """Test the API for PCE educational modules.

    Class attrs:
        modules_dir (str): Relative path to deployed modules base dir.
        testmodule_dir (str): Relative path to deployed testing module dir.
    
    Methods:
        test_POST: Test resource response to various POST requests.
    """
    def setUp(self):
        self.username = test_ini['username']
        self.run_name = test_ini['run_name']
        self.modules_dir = '../../modules'
        self.testmodule_dir = self.modules_dir + '/testmodule'
        self.run_dir = ('../../users/%s/%s/%s'
                        % (self.username, 'testmodule', self.run_name))
        self.run_dir2 = self.run_dir + 'second'
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

        if(os.path.isdir(self.run_dir)):
            shutil.rmtree(self.run_dir)
        if(os.path.isdir(self.run_dir2)):
            shutil.rmtree(self.run_dir2)

    def test_POST(self):
        """Test resource response to various POST requests."""
        rel_url = ('/jobs/%s_%s_%s/' 
                   % (self.username, 'testmodule', self.run_name))
        rel_url2 = ('/jobs/%s_%s_%s/' 
                    % (self.username, 'testmodule', self.run_name+'second'))
        success_response_fields = [u'job_num']
        error_response_fields = []

        # Request under normal conditions:
        r = pce_post('jobs/', username=self.username, module_name='testmodule',
                     run_name=self.run_name)
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_base_JSON_attrs(d)
        self.assertIn(u'job_num', d.keys())
        self.assertEqual(d['status_code'], 0)
        test_str = ('Job %s_%s_%s scheduled as job_num: '
                    % (self.username, 'testmodule', self.run_name))
        self.assertTrue(d['status_msg'].startswith(test_str))
        fields = d['status_msg'].split(test_str)
        self.assertEqual(len(fields), 2)
        self.assertEqual(int(fields[1]), d['job_num'])
        self.assertTrue(os.path.isdir(self.run_dir))
        self.assertTrue(os.path.isdir(self.run_dir + '/.onramp'))
        self.assertTrue(os.path.isfile(self.run_dir + '/.onramp/run_info'))
        conf = ConfigObj(self.run_dir + '/.onramp/run_info')
        conf_keys = conf.keys()
        self.assertIn('job_num', conf_keys)
        self.assertIn('job_state', conf_keys)
        self.assertIn('module_name', conf_keys)
        self.assertEqual(conf['job_num'], str(d['job_num']))
        self.assertEqual(conf['job_state'], 'Queued')
        self.assertEqual(conf['module_name'], 'testmodule')
        self.assertTrue(os.path.isfile(self.run_dir + '/script.sh'))
        self.assertTrue(d['url'].endswith(rel_url))
        fields = success_response_fields + self.base_response_fields
        for k in d.keys():
            self.assertIn(k, fields)
        time.sleep(1)
        self.assertTrue(os.path.isfile(self.run_dir + '/output.txt'))
        with open(self.run_dir + '/output.txt', 'r') as f:
            output = f.read()
            expected = ('Testing output from testmodule.Testing output from '
                        'testmodule.Testing output from testmodule.Testing '
                        'output from testmodule.')
            self.assertEqual(output, expected)

        # Request with same attrs as previously run job:
        r = pce_post('jobs/', username=self.username, module_name='testmodule',
                     run_name=self.run_name)
        self.assertEqual(r.status_code, 400)
        d = r.json()
        self.check_base_JSON_attrs(d)
        self.assertEqual(d['status_code'], -3)
        self.assertEqual(d['status_msg'], 'A job with this name already exists')
        self.assertTrue(d['url'].endswith(rel_url))
        fields = error_response_fields + self.base_response_fields
        for k in d.keys():
            self.assertIn(k, fields)

        # Request new job w/ same module but different run_name:
        r = pce_post('jobs/', username=self.username, module_name='testmodule',
                     run_name=self.run_name+'second')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_base_JSON_attrs(d)
        self.assertIn(u'job_num', d.keys())
        self.assertEqual(d['status_code'], 0)
        test_str = ('Job %s_%s_%s scheduled as job_num: '
                    % (self.username, 'testmodule', self.run_name+'second'))
        self.assertTrue(d['status_msg'].startswith(test_str))
        fields = d['status_msg'].split(test_str)
        self.assertEqual(len(fields), 2)
        self.assertEqual(int(fields[1]), d['job_num'])
        self.assertTrue(os.path.isdir(self.run_dir2))
        self.assertTrue(os.path.isdir(self.run_dir2 + '/.onramp'))
        self.assertTrue(os.path.isfile(self.run_dir2 + '/.onramp/run_info'))
        conf = ConfigObj(self.run_dir2 + '/.onramp/run_info')
        conf_keys = conf.keys()
        self.assertIn('job_num', conf_keys)
        self.assertIn('job_state', conf_keys)
        self.assertIn('module_name', conf_keys)
        self.assertEqual(conf['job_num'], str(d['job_num']))
        self.assertEqual(conf['job_state'], 'Queued')
        self.assertEqual(conf['module_name'], 'testmodule')
        self.assertTrue(os.path.isfile(self.run_dir + '/script.sh'))
        self.assertTrue(d['url'].endswith(rel_url2))
        fields = success_response_fields + self.base_response_fields
        for k in d.keys():
            self.assertIn(k, fields)
        time.sleep(1)
        self.assertTrue(os.path.isfile(self.run_dir2 + '/output.txt'))
        with open(self.run_dir2 + '/output.txt', 'r') as f:
            output = f.read()
            expected = ('Testing output from testmodule.Testing output from '
                        'testmodule.Testing output from testmodule.Testing '
                        'output from testmodule.')
            self.assertEqual(output, expected)

        # Requests with missing params:
        r = pce_post('jobs/', module_name='testmodule', run_name=self.run_name)
        self.assertEqual(r.status_code, 400)
        d = r.json()
        self.check_base_JSON_attrs(d)
        self.assertEqual(d['status_code'], -8)
        msg = ('An invalid value was received for the following required '
               'parameter(s): username')
        self.assertEqual(d['status_msg'], msg)

        r = pce_post('jobs/', username=self.username, module_name='testmodule')
        self.assertEqual(r.status_code, 400)
        d = r.json()
        self.check_base_JSON_attrs(d)
        self.assertEqual(d['status_code'], -8)
        msg = ('An invalid value was received for the following required '
               'parameter(s): run_name')
        self.assertEqual(d['status_msg'], msg)

        r = pce_post('jobs/', username=self.username, run_name=self.run_name)
        self.assertEqual(r.status_code, 400)
        d = r.json()
        self.check_base_JSON_attrs(d)
        self.assertEqual(d['status_code'], -8)
        msg = ('An invalid value was received for the following required '
               'parameter(s): module_name')
        self.assertEqual(d['status_msg'], msg)

        r = pce_post('jobs/', module_name='testmodule')
        self.assertEqual(r.status_code, 400)
        d = r.json()
        self.check_base_JSON_attrs(d)
        self.assertEqual(d['status_code'], -8)
        msg = ('An invalid value was received for the following required '
               'parameter(s)')
        parts = d['status_msg'].split(': ')
        self.assertEqual(parts[0], msg)
        expected = ['username', 'run_name']
        found = parts[1].split(', ')
        for item in expected:
            self.assertIn(item, found)
        for item in found:
            self.assertIn(item, expected)

        r = pce_post('jobs/', username=self.username)
        self.assertEqual(r.status_code, 400)
        d = r.json()
        self.check_base_JSON_attrs(d)
        self.assertEqual(d['status_code'], -8)
        parts = d['status_msg'].split(': ')
        self.assertEqual(parts[0], msg)
        expected = ['module_name', 'run_name']
        found = parts[1].split(', ')
        for item in expected:
            self.assertIn(item, found)
        for item in found:
            self.assertIn(item, expected)

        r = pce_post('jobs/', run_name=self.run_name)
        self.assertEqual(r.status_code, 400)
        d = r.json()
        self.check_base_JSON_attrs(d)
        self.assertEqual(d['status_code'], -8)
        parts = d['status_msg'].split(': ')
        self.assertEqual(parts[0], msg)
        expected = ['username', 'module_name']
        found = parts[1].split(', ')
        for item in expected:
            self.assertIn(item, found)
        for item in found:
            self.assertIn(item, expected)

        # FIXME: Figure out a way to test the following:
        # - Execution of batch schedule call fails.
        # - Output from batch schedule call not formatted as expected.
        # - Bad batch scheduler optoin in config (though this should be caught
        #   by the Validator when config is loaded.
        # - Missing inputspec file

        # Check to make sure no exceptions and proper response when module not
        # found:
        shutil.rmtree(self.modules_dir)
        os.mkdir(self.modules_dir)
        r = pce_post('jobs/', username=self.username, module_name='testmodule',
                     run_name=self.run_name)
        self.assertEqual(r.status_code, 404)
        d = r.json()
        self.check_base_JSON_attrs(d)
        self.assertEqual(d['status_code'], -2)
        self.assertEqual(d['status_msg'], 'Module testmodule does not exist')
        self.assertTrue(d['url'].endswith('/jobs/'))
        self.assertNotIn('module', d.keys())
        self.assertNotIn('modules', d.keys())

        # Check proper status code and message given when modules dir missing:
        shutil.rmtree(self.modules_dir)
        r = pce_post('jobs/', username=self.username, module_name='testmodule',
                     run_name=self.run_name)
        self.assertEqual(r.status_code, 500)
        d = r.json()
        self.check_base_JSON_attrs(d)
        self.assertEqual(d['status_code'], -1)
        self.assertEqual(d['status_msg'], 'Modules root folder does not exist')
        self.assertTrue(d['url'].endswith('/jobs/'))
        self.assertNotIn('modules', d.keys())
        self.assertNotIn('module', d.keys())
