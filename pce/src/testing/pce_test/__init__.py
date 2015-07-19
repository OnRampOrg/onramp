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
import unittest
from configobj import ConfigObj
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

def pce_get(endpoint, **kwargs):
    """Execute a GET to the specified endpoint.

    Args:
        enpoint (str): Endpoint of the resource reqested.

    Kwargs: Keys/vals encode as JSON and send with request.
    """
    return requests.get(pce_url(endpoint), params=kwargs)

def pce_post(endpoint, **kwargs):
    """Execute a POST to the specified endpoint.

    Args:
        enpoint (str): Endpoint of the resource reqested.

    Kwargs: Keys/vals encode as JSON and send with request.
    """
    return requests.post(pce_url(endpoint), data=json.dumps(kwargs),
                         headers={'content-type': 'application/json'})

def pce_put(endpoint, **kwargs):
    """Execute a PUT to the specified endpoint.

    Args:
        enpoint (str): Endpoint of the resource reqested.

    Kwargs: Keys/vals encode as JSON and send with request.
    """
    return requests.put(pce_url(endpoint), data=json.dumps(kwargs),
                        headers={'content-type': 'application/json'})

def pce_delete(endpoint, **kwargs):
    """Execute a DELETE to the specified endpoint.

    Args:
        enpoint (str): Endpoint of the resource reqested.

    Kwargs: Keys/vals encode as JSON and send with request.
    """
    return requests.delete(pce_url(endpoint), data=json.dumps(kwargs),
                        headers={'content-type': 'application/json'})


class PCEBase(unittest.TestCase):
    def check_json(self, d, good=False):
        self.assertIsNotNone(d)
        self.assertIn('status_code', d.keys())
        self.assertIn('status_msg', d.keys())

        if good:
            self.assertEqual(d['status_code'], 0)
            self.assertEqual(d['status_msg'], 'Success')

class ModulesTest(PCEBase):
    def test_GET(self):
        r = pce_get('modules/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d, good=True)

        r = pce_get('modules/1/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d, good=True)

        r = pce_get('modules/', test=88)
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d, good=True)

        r = pce_get('modules/45/99/')
        self.assertEqual(r.status_code, 404)

        r = pce_get('modules/45/99/', test=88)
        self.assertEqual(r.status_code, 404)

    def test_POST(self):
        missing_msg_prefix = ('An invalid value or no value was received for the '
                              'following required parameter(s): ')

        r = pce_post('modules/1/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d, good=True)

        r = pce_post('modules/', mod_id=3, mod_name='testname',
                     location={'code':0, 'path':'test/path'})
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d, good=True)

        r = pce_post('modules/', mod_id=3, mod_name='testname',
                     location={'code':0, 'path':'test/path'},
                     dummy_param='dummy')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d, good=True)

        r = pce_post('modules/', mod_name='testname',
                     location={'code':0, 'path':'test/path'})
        self.assertEqual(r.status_code, 400)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], -8)
        self.assertTrue(d['status_msg'].startswith(missing_msg_prefix))
        missing_params = d['status_msg'].split(missing_msg_prefix)[1].split(', ')
        self.assertIn('mod_id', missing_params)

        r = pce_post('modules/', mod_id=3,
                     location={'code':0, 'path':'test/path'})
        self.assertEqual(r.status_code, 400)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], -8)
        self.assertTrue(d['status_msg'].startswith(missing_msg_prefix))
        missing_params = d['status_msg'].split(missing_msg_prefix)[1].split(', ')
        self.assertIn('mod_name', missing_params)

        r = pce_post('modules/', mod_id=3, mod_name='testname')
        self.assertEqual(r.status_code, 400)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], -8)
        self.assertTrue(d['status_msg'].startswith(missing_msg_prefix))
        missing_params = d['status_msg'].split(missing_msg_prefix)[1].split(', ')
        self.assertIn('location', missing_params)

        r = pce_post('modules/', mod_id=3, mod_name='testname',
                     location={'path':'test/path'})
        self.assertEqual(r.status_code, 400)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], -8)
        self.assertTrue(d['status_msg'].startswith(missing_msg_prefix))
        missing_params = d['status_msg'].split(missing_msg_prefix)[1].split(', ')
        self.assertIn('[location]code', missing_params)

        r = pce_post('modules/', mod_id=3, mod_name='testname',
                     location={'code':0})
        self.assertEqual(r.status_code, 400)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], -8)
        self.assertTrue(d['status_msg'].startswith(missing_msg_prefix))
        missing_params = d['status_msg'].split(missing_msg_prefix)[1].split(', ')
        self.assertIn('[location]path', missing_params)

        r = pce_post('modules/', mod_id=3, mod_name='testname', location={})
        self.assertEqual(r.status_code, 400)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], -8)
        self.assertTrue(d['status_msg'].startswith(missing_msg_prefix))
        missing_params = d['status_msg'].split(missing_msg_prefix)[1].split(', ')
        self.assertIn('[location]code', missing_params)
        self.assertIn('[location]path', missing_params)

        r = pce_post('modules/', location={'path':'test/path'})
        self.assertEqual(r.status_code, 400)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], -8)
        self.assertTrue(d['status_msg'].startswith(missing_msg_prefix))
        missing_params = d['status_msg'].split(missing_msg_prefix)[1].split(', ')
        self.assertIn('mod_id', missing_params)
        self.assertIn('mod_name', missing_params)
        self.assertIn('[location]code', missing_params)

        r = pce_post('modules/')
        self.assertEqual(r.status_code, 400)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], -8)
        self.assertTrue(d['status_msg'].startswith(missing_msg_prefix))
        missing_params = d['status_msg'].split(missing_msg_prefix)[1].split(', ')
        self.assertIn('mod_id', missing_params)
        self.assertIn('mod_name', missing_params)
        self.assertIn('location', missing_params)

        r = pce_post('modules/1/1/')
        self.assertEqual(r.status_code, 404)

    def test_PUT(self):
        r = pce_put('modules/')
        self.assertEqual(r.status_code, 404)

        r = pce_put('modules/1/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d, good=True)

        r = pce_put('modules/1/1/')
        self.assertEqual(r.status_code, 404)

    def test_DELETE(self):
        r = pce_delete('modules/')
        self.assertEqual(r.status_code, 404)

        r = pce_delete('modules/1/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d, good=True)

        r = pce_delete('modules/1/1/')
        self.assertEqual(r.status_code, 404)


class JobsTest(PCEBase):
    def test_GET(self):
        r = pce_get('jobs/')
        self.assertEqual(r.status_code, 404)

        r = pce_get('jobs/1/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d, good=True)

        r = pce_get('jobs/45/99/')
        self.assertEqual(r.status_code, 404)

    def test_POST(self):
        missing_msg_prefix = ('An invalid value or no value was received for the '
                              'following required parameter(s): ')

        r = pce_post('jobs/', mod_id=1, job_id=1, username='testuser')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d, good=True)

        r = pce_post('jobs/', job_id=1, username='testuser')
        self.assertEqual(r.status_code, 400)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], -8)
        self.assertTrue(d['status_msg'].startswith(missing_msg_prefix))
        missing_params = d['status_msg'].split(missing_msg_prefix)[1].split(', ')
        self.assertIn('mod_id', missing_params)

        r = pce_post('jobs/', mod_id=1, username='testuser')
        self.assertEqual(r.status_code, 400)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], -8)
        self.assertTrue(d['status_msg'].startswith(missing_msg_prefix))
        missing_params = d['status_msg'].split(missing_msg_prefix)[1].split(', ')
        self.assertIn('job_id', missing_params)

        r = pce_post('jobs/', mod_id=1, job_id=1)
        self.assertEqual(r.status_code, 400)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], -8)
        self.assertTrue(d['status_msg'].startswith(missing_msg_prefix))
        missing_params = d['status_msg'].split(missing_msg_prefix)[1].split(', ')
        self.assertIn('username', missing_params)

        r = pce_post('jobs/', mod_id=1)
        self.assertEqual(r.status_code, 400)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], -8)
        self.assertTrue(d['status_msg'].startswith(missing_msg_prefix))
        missing_params = d['status_msg'].split(missing_msg_prefix)[1].split(', ')
        self.assertIn('job_id', missing_params)
        self.assertIn('username', missing_params)

        r = pce_post('jobs/', job_id=1)
        self.assertEqual(r.status_code, 400)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], -8)
        self.assertTrue(d['status_msg'].startswith(missing_msg_prefix))
        missing_params = d['status_msg'].split(missing_msg_prefix)[1].split(', ')
        self.assertIn('mod_id', missing_params)
        self.assertIn('username', missing_params)

        r = pce_post('jobs/', username='testuser')
        self.assertEqual(r.status_code, 400)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], -8)
        self.assertTrue(d['status_msg'].startswith(missing_msg_prefix))
        missing_params = d['status_msg'].split(missing_msg_prefix)[1].split(', ')
        self.assertIn('mod_id', missing_params)
        self.assertIn('job_id', missing_params)

        r = pce_post('jobs/')
        self.assertEqual(r.status_code, 400)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], -8)
        self.assertTrue(d['status_msg'].startswith(missing_msg_prefix))
        missing_params = d['status_msg'].split(missing_msg_prefix)[1].split(', ')
        self.assertIn('mod_id', missing_params)
        self.assertIn('job_id', missing_params)
        self.assertIn('username', missing_params)

        r = pce_post('jobs/45/')
        self.assertEqual(r.status_code, 404)

    def test_PUT(self):
        r = pce_put('jobs/')
        self.assertEqual(r.status_code, 404)

        r = pce_put('jobs/1/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d, good=True)

        r = pce_put('jobs/1/1/')
        self.assertEqual(r.status_code, 404)

    def test_DELETE(self):
        r = pce_delete('jobs/')
        self.assertEqual(r.status_code, 404)

        r = pce_delete('jobs/1/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d, good=True)

        r = pce_delete('jobs/1/1/')
        self.assertEqual(r.status_code, 404)


class ClusterTest(PCEBase):
    def test_GET(self):
        r = pce_get('cluster/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d, good=True)

        r = pce_get('cluster/1/')
        self.assertEqual(r.status_code, 404)

    def test_POST(self):
        r = pce_post('cluster/')
        self.assertEqual(r.status_code, 405)

        r = pce_post('cluster/1/')
        self.assertEqual(r.status_code, 405)

    def test_PUT(self):
        r = pce_put('cluster/1/')
        self.assertEqual(r.status_code, 405)

        r = pce_put('cluster/1/')
        self.assertEqual(r.status_code, 405)

    def test_DELETE(self):
        r = pce_delete('cluster/1/')
        self.assertEqual(r.status_code, 405)

        r = pce_delete('cluster/1/')
        self.assertEqual(r.status_code, 405)
