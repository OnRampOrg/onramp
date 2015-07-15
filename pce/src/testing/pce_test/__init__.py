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
    return requests.get(pce_url(endpoint), data=kwargs,
                        headers={'content-type': 'application/json'})

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
    return requests.put(pce_url(endpoint), data=kwargs,
                        headers={'content-type': 'application/json'})

def pce_delete(endpoint, **kwargs):
    """Execute a DELETE to the specified endpoint.

    Args:
        enpoint (str): Endpoint of the resource reqested.

    Kwargs: Keys/vals encode as JSON and send with request.
    """
    return requests.delete(pce_url(endpoint), data=kwargs,
                        headers={'content-type': 'application/json'})


class ModulesTest(unittest.TestCase):
    def test_GET(self):
        r = pce_get('modules/')
        self.assertEqual(r.status_code, 200)
        r = pce_get('modules/', dummy_param=7)
        self.assertEqual(r.status_code, 200)

#    def test_POST(self):
#        r = pce_post('modules/')
#        self.assertEqual(r.status_code, 200)
#
#    def test_PUT(self):
#        r = pce_put('modules/')
#        self.assertEqual(r.status_code, 400)
#
#    def test_DELETE(self):
#        r = pce_delete('modules/')
#        self.assertEqual(r.status_code, 404)


class ParticularModuleTest(unittest.TestCase):
    def test_GET(self):
        r = pce_get('modules/1/')
        self.assertEqual(r.status_code, 200)
        r = pce_get('modules/1/', dummy_param=7)
        self.assertEqual(r.status_code, 200)

#    def test_POST(self):
#        r = pce_post('modules/1/')
#        self.assertEqual(r.status_code, 400)
#
#    def test_PUT(self):
#        r = pce_put('modules/1/')
#        self.assertEqual(r.status_code, 200)
#
#    def test_DELETE(self):
#        r = pce_delete('modules/1/')
#        self.assertEqual(r.status_code, 200)


class JobsTest(unittest.TestCase):
    __test__ = False
    def test_GET(self):
        r = pce_get('jobs/')
        self.assertEqual(r.status_code, 404)

    def test_POST(self):
        r = pce_post('jobs/')
        self.assertEqual(r.status_code, 200)

    def test_PUT(self):
        r = pce_put('jobs/')
        self.assertEqual(r.status_code, 400)

    def test_DELETE(self):
        r = pce_delete('jobs/')
        self.assertEqual(r.status_code, 404)


class ParticularJobTest(unittest.TestCase):
    __test__ = False
    def test_GET(self):
        r = pce_get('jobs/1/')
        self.assertEqual(r.status_code, 200)

    def test_POST(self):
        r = pce_post('jobs/1/')
        self.assertEqual(r.status_code, 404)

    def test_PUT(self):
        r = pce_put('jobs/1/')
        self.assertEqual(r.status_code, 200)

    def test_DELETE(self):
        r = pce_delete('jobs/1/')
        self.assertEqual(r.status_code, 200)


class ClusterTest(unittest.TestCase):
    __test__ = False
    def test_GET(self):
        r = pce_get('cluster/')
        self.assertEqual(r.status_code, 200)

    def test_POST(self):
        r = pce_post('cluster/')
        self.assertEqual(r.status_code, 405)

    def test_PUT(self):
        r = pce_put('cluster/')
        self.assertEqual(r.status_code, 400)

    def test_DELETE(self):
        r = pce_delete('cluster/')
        self.assertEqual(r.status_code, 405)
