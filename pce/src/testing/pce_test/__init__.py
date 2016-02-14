"""Unit testing and testing environment setup for OnRamp PCE.

Exports:
    setup: Setup the testing environment.
    pce_url: Build the full URL for the resource at a specified endpoint.
    pce_post: Execute a POST request to a given endpoint with given params.
    pce_get: Execute a GET request to a given endpoint with given params.
    ModulesTest: Unit tests for the PCE modules resource.
    JobsTest: Unit tests for the PCE jobs resource.
    ClusterTest: Unit tests for the PCE cluster resource.
"""
import json
import os
import requests
import shutil
import time
import unittest

from configobj import ConfigObj
from validate import Validator

from PCE.tools.jobs import JobState
from PCE.tools.modules import ModState
from PCEHelper import pce_root

def setup():
    """Setup the testing environment."""
    global onramp_cfg
    global test_cfg

    specfile ='../configspecs/onramp_pce_config.cfgspec'
    onramp_cfg = ConfigObj('../../bin/onramp_pce_config.cfg',
                           configspec=specfile)
    onramp_cfg.validate(Validator())
    test_cfg = ConfigObj('test_pce_config.cfg',
                         configspec='test_pce_config.cfgspec')
    test_cfg.validate(Validator())

def pce_url(endpoint):
    """Build the full URL for the resource at the specified endpoint.

    Args:
        enpoint (str): Endpoint of the resource reqested.
    """
    return ('http://%s:%d/%s' % (onramp_cfg['server']['socket_host'],
                                 onramp_cfg['server']['socket_port'],
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
    def setUp(self):
        self.ret_dir = os.getcwd()
        os.chdir(pce_root)
        self.source_dir = '../modules'
        self.mod_state_dir = 'src/state/modules'
        self.job_state_dir = 'src/state/jobs'
        self.install_dir = 'modules'
        self.users_dir = 'users'
        self.avail_mods = ['template', 'mpi-ring', 'AUC']

        def not_hidden(x):
            return not x.startswith('.')

        for name in os.listdir(self.install_dir):
            shutil.rmtree('%s/%s' % (self.install_dir, name))
        for name in filter(not_hidden, os.listdir(self.mod_state_dir)):
            os.remove('%s/%s' % (self.mod_state_dir, name))
        for name in filter(not_hidden, os.listdir(self.job_state_dir)):
            os.remove('%s/%s' % (self.job_state_dir, name))
        for name in os.listdir(self.users_dir):
            shutil.rmtree('%s/%s' % (self.users_dir, name))
        time.sleep(5)

    def tearDown(self):
        os.chdir(self.ret_dir)

    def check_json(self, d, good=False):
        self.assertIsNotNone(d)
        self.assertIn('status_code', d.keys())
        self.assertIn('status_msg', d.keys())

        if good:
            self.assertEqual(d['status_code'], 0)
            self.assertEqual(d['status_msg'], 'Success')

class ModulesTest(PCEBase):
    #__test__ = False
    def verify_mod_install(self, id, name):
        with ModState(id) as mod_state:
            temp_path = os.path.join(pce_root, self.install_dir)
            installed_path = os.path.join(temp_path, '%s_%s' %(name, id))
            temp_path = os.path.join(pce_root, self.source_dir)
            source_path = os.path.normpath(os.path.join(temp_path, name))

            self.assertEqual(mod_state['mod_id'], id)
            self.assertEqual(mod_state['mod_name'], name)
            self.assertEqual(mod_state['state'], 'Installed')
            self.assertIsNone(mod_state['error'])
            self.assertEqual(mod_state['installed_path'], installed_path)
            self.assertEqual(mod_state['source_location']['type'], 'local')
            self.assertEqual(mod_state['source_location']['path'], source_path)

    def verify_avail_mod(self, mod):
        src_dir_root = os.path.normpath(os.path.abspath(self.source_dir))
        self.assertEqual(mod['source_location'],
                         {'type': 'local',
                          'path': os.path.join(src_dir_root, mod['mod_name'])})
        self.assertEqual(mod['state'], 'Available')
        self.assertIsNone(mod['installed_path'])
        self.assertIsNone(mod['error'])
        self.assertIsNone(mod['mod_id'])

    def test_GET(self):
        template_path = os.path.normpath(os.path.join(pce_root,
                                                      '../modules/template'))
        mpi_ring_path = os.path.normpath(os.path.join(pce_root,
                                                      '../modules/mpi-ring'))
        location = {
            'type': 'local',
            'path': template_path
        }

        installed_mods = {
            1: {
                'mod_id': 1,
                'mod_name': 'template',
                'source_location': {
                    'type': 'local',
                    'path': template_path
                }
            },
            2: {
                'mod_id': 2,
                'mod_name': 'template',
                'source_location': {
                    'type': 'local',
                    'path': template_path
                }
            },
            3: {
                'mod_id': 3,
                'mod_name': 'mpi-ring',
                'source_location': {
                    'type': 'local',
                    'path': mpi_ring_path
                }
            },
            4: {
                'mod_id': 4,
                'mod_name': 'mpi-ring',
                'source_location': {
                    'type': 'local',
                    'path': mpi_ring_path
                }
            }
        }

        mod_state_files = filter(lambda x: not x.startswith('.'),
                                 os.listdir(self.mod_state_dir))
        self.assertEqual(mod_state_files, [])

        # Check installed mods. Should be empty.
        r = pce_get('modules/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d, good=True)
        self.assertListEqual(d['modules'], [])

        # Check available mods. Should be shipped modules only.
        r = pce_get('modules/', state='Available')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d, good=True)
        self.assertEqual(len(d['modules']), len(self.avail_mods))
        for mod in d['modules']:
            self.assertIn(mod['mod_name'], self.avail_mods)
            self.verify_avail_mod(mod)

        # Install some mods.
        for k in installed_mods.keys():
            r = pce_post('modules/', **installed_mods[k])
            self.assertEqual(r.status_code, 200)
            d = r.json()
            self.check_json(d)
            self.assertEqual(d['status_code'], 0)
            self.assertEqual(d['status_msg'], 'Checkout initiated')
        time.sleep(10)

        # Get installed mods.
        r = pce_get('modules/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d, good=True)
        self.assertEqual(len(d['modules']), len(installed_mods.keys()))
        rxd_mods = {mod['mod_id']: mod for mod in d['modules']}
        self.assertEqual(len(rxd_mods.keys()), len(installed_mods.keys()))

        # Verify each mod has proper attrs and that attrs match result rxd
        # on GET modules/.
        install_dir = os.path.normpath(os.path.join(pce_root, self.install_dir))
        for k in installed_mods.keys():
            install_path = os.path.join(
                install_dir, '%s_%s' % (installed_mods[k]['mod_name'], k)
            )
            r = pce_get('modules/%d/' % k)
            self.assertEqual(r.status_code, 200)
            d = r.json()
            self.check_json(d, good=True)
            mod = d['module']
            self.assertEqual(mod['mod_id'], k)
            self.assertEqual(mod['mod_name'], installed_mods[k]['mod_name'])
            self.assertEqual(mod['source_location'],
                             installed_mods[k]['source_location'])
            self.assertEqual(mod['state'], 'Installed')
            self.assertEqual(mod['installed_path'], install_path)
            self.assertIsNone(mod['error'])
            self.assertEqual(mod, rxd_mods[k])

        # Install and deploy module to allow testing of uioptions
        testmodule_path = os.path.normpath(os.path.join(pce_root,
                                                    'src/testing/testmodule2'))
        location = {
            'type': 'local',
            'path': testmodule_path
        }
        install_path = os.path.join(install_dir, '%s_%d' % ('testmodule2_ui',
                                                            10))
        conf = ConfigObj(os.path.join(location['path'],
                                      'config/onramp_uioptions.cfgspec'))
        expected_conf = conf.dict()
        self.assertIsNotNone(expected_conf)
        r = pce_post('modules/', mod_id=10, mod_name='testmodule2_ui',
                     source_location=location)
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], 0)
        self.assertEqual(d['status_msg'], 'Checkout initiated')
        time.sleep(3)
        r = pce_post('modules/10/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d)
        time.sleep(4)
        r = pce_get('modules/10/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d, good=True)
        self.assertIn('module', d.keys())
        mod = d['module']
        self.assertEqual(mod['mod_id'], 10)
        self.assertEqual(mod['mod_name'], 'testmodule2_ui')
        self.assertEqual(mod['source_location'], location)
        self.assertEqual(mod['state'], 'Module ready')
        self.assertEqual(mod['installed_path'], install_path)
        self.assertEqual(mod['uioptions'], expected_conf)
        self.assertIsNone(mod['error'])

        # Bad URL
        r = pce_get('modules/45/99/')
        self.assertEqual(r.status_code, 404)

    def test_POST(self):
        missing_msg_prefix = ('An invalid value or no value was received for the '
                              'following required parameter(s): ')

        template_path = os.path.normpath(os.path.join(pce_root,
                                                      '../modules/template'))
        location = {
            'type': 'local',
            'path': template_path
        }

        # Good post of new mod
        r = pce_post('modules/', mod_id=3, mod_name='template',
                     source_location=location)
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], 0)
        self.assertEqual(d['status_msg'], 'Checkout initiated')

        # Good post of 2nd new mod
        r = pce_post('modules/', mod_id=4, mod_name='template',
                     source_location=location)
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], 0)
        self.assertEqual(d['status_msg'], 'Checkout initiated')

        # Verify stored state for new mods
        time.sleep(10)
        self.verify_mod_install(3, 'template')
        self.verify_mod_install(4, 'template')

        # Attempt to post with already existing id
        r = pce_post('modules/', mod_id=3, mod_name='template',
                     source_location=location)
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], 0)
        self.assertEqual(d['status_msg'], 'Checkout initiated')
        self.verify_mod_install(3, 'template')

        # Attempt to post with already existing id, but different mod name
        r = pce_post('modules/', mod_id=3, mod_name='mpi-ring',
                     source_location=location)
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], 0)
        self.assertEqual(d['status_msg'], 'Checkout initiated')
        self.verify_mod_install(3, 'template')

        # Attempt with bad source type
        location['type'] = 'bad'
        r = pce_post('modules/', mod_id=5, mod_name='template',
                     source_location=location)
        self.assertEqual(r.status_code, 400)

        # Attempt with bad source path
        location['type'] = 'local'
        location['path'] = os.path.normpath(
                            os.path.join(pce_root, '../modules/bad_path'))
        r = pce_post('modules/', mod_id=5, mod_name='template',
                     source_location=location)
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], 0)
        self.assertEqual(d['status_msg'], 'Checkout initiated')
        time.sleep(10)
        with ModState(5) as mod_state:
            self.assertEqual(mod_state['mod_id'], 5)
            self.assertEqual(mod_state['mod_name'], 'template')
            self.assertEqual(mod_state['state'], 'Checkout failed')
            self.assertEqual(mod_state['error'],
                             'Source path %s does not exist' % location['path'])
            self.assertIsNone(mod_state['installed_path'])
            self.assertEqual(mod_state['source_location']['type'], 'local')
            self.assertEqual(mod_state['source_location']['path'], location['path'])
        
        # Reattempt previous with good source path, ensure mod state gets
        # updated
        location['path'] = template_path
        r = pce_post('modules/', mod_id=5, mod_name='template',
                     source_location=location)
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], 0)
        self.assertEqual(d['status_msg'], 'Checkout initiated')
        time.sleep(10)
        self.verify_mod_install(5, 'template')

        # Attempt deploy that should work
        r = pce_post('modules/5/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], 0)
        self.assertEqual(d['status_msg'], 'Deployment initiated')
        mod_path = os.path.normpath(os.path.join(pce_root,
                                                 'modules/template_5'))
        time.sleep(10)
        with ModState(5) as mod_state:
            self.assertEqual(mod_state['state'], 'Module ready')
            self.assertIsNone(mod_state['error'])
            self.assertEqual(mod_state['source_location']['type'], 'local')
            self.assertEqual(mod_state['source_location']['path'],
                             location['path'])
            self.assertEqual(mod_state['installed_path'], mod_path)
            self.assertEqual(mod_state['mod_id'], 5)
            self.assertEqual(mod_state['mod_name'], 'template')

        # Re-attempt deploy that already happened.
        r = pce_post('modules/5/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], 0)
        self.assertEqual(d['status_msg'], 'Deployment initiated')
        mod_path = os.path.normpath(os.path.join(pce_root,
                                                 'modules/template_5'))
        time.sleep(10)
        with ModState(5) as mod_state:
            self.assertEqual(mod_state['state'], 'Module ready')
            self.assertIsNone(mod_state['error'])
            self.assertEqual(mod_state['source_location']['type'], 'local')
            self.assertEqual(mod_state['source_location']['path'],
                             location['path'])
            self.assertEqual(mod_state['installed_path'], mod_path)
            self.assertEqual(mod_state['mod_id'], 5)
            self.assertEqual(mod_state['mod_name'], 'template')

        # Attempt deployment of non-existent mod_id.
        r = pce_post('modules/15/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], -2)
        self.assertEqual(d['status_msg'], 'Module 15 not installed')
        mod_path = os.path.normpath(os.path.join(pce_root,
                                                 'modules/template_15'))

        # Attempt with missing mod_id
        r = pce_post('modules/', mod_name='testname',
                     source_location={'type':0, 'path':'test/path'})
        self.assertEqual(r.status_code, 400)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], -8)
        self.assertTrue(d['status_msg'].startswith(missing_msg_prefix))
        missing_params = d['status_msg'].split(missing_msg_prefix)[1].split(', ')
        self.assertIn('mod_id', missing_params)

        # Attempt with missing mod_name
        r = pce_post('modules/', mod_id=3,
                     source_location={'type': 'local', 'path':'test/path'})
        self.assertEqual(r.status_code, 400)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], -8)
        self.assertTrue(d['status_msg'].startswith(missing_msg_prefix))
        missing_params = d['status_msg'].split(missing_msg_prefix)[1].split(', ')
        self.assertIn('mod_name', missing_params)

        # Attempt with missing source_location
        r = pce_post('modules/', mod_id=3, mod_name='testname')
        self.assertEqual(r.status_code, 400)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], -8)
        self.assertTrue(d['status_msg'].startswith(missing_msg_prefix))
        missing_params = d['status_msg'].split(missing_msg_prefix)[1].split(', ')
        self.assertIn('source_location', missing_params)

        # Attempt with missing source_location['type']
        r = pce_post('modules/', mod_id=3, mod_name='testname',
                     source_location={'path':'test/path'})
        self.assertEqual(r.status_code, 400)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], -8)
        self.assertTrue(d['status_msg'].startswith(missing_msg_prefix))
        missing_params = d['status_msg'].split(missing_msg_prefix)[1].split(', ')
        self.assertIn('[source_location]type', missing_params)

        # Attempt with missing source_location['path']
        r = pce_post('modules/', mod_id=3, mod_name='testname',
                     source_location={'type': 'local'})
        self.assertEqual(r.status_code, 400)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], -8)
        self.assertTrue(d['status_msg'].startswith(missing_msg_prefix))
        missing_params = d['status_msg'].split(missing_msg_prefix)[1].split(', ')
        self.assertIn('[source_location]path', missing_params)

        # Attempt with empty source_location
        r = pce_post('modules/', mod_id=3, mod_name='testname', source_location={})
        self.assertEqual(r.status_code, 400)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], -8)
        self.assertTrue(d['status_msg'].startswith(missing_msg_prefix))
        missing_params = d['status_msg'].split(missing_msg_prefix)[1].split(', ')
        self.assertIn('[source_location]type', missing_params)
        self.assertIn('[source_location]path', missing_params)

        # Attempt with missing mod_id, mod_name, and source_location['type']
        r = pce_post('modules/', source_location={'path':'test/path'})
        self.assertEqual(r.status_code, 400)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], -8)
        self.assertTrue(d['status_msg'].startswith(missing_msg_prefix))
        missing_params = d['status_msg'].split(missing_msg_prefix)[1].split(', ')
        self.assertIn('mod_id', missing_params)
        self.assertIn('mod_name', missing_params)
        self.assertIn('[source_location]type', missing_params)

        # Attempt with none of the required params
        r = pce_post('modules/')
        self.assertEqual(r.status_code, 400)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], -8)
        self.assertTrue(d['status_msg'].startswith(missing_msg_prefix))
        missing_params = d['status_msg'].split(missing_msg_prefix)[1].split(', ')
        self.assertIn('mod_id', missing_params)
        self.assertIn('mod_name', missing_params)
        self.assertIn('source_location', missing_params)

        # Attempt with bad URL
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

        r = pce_delete('modules/1/1/')
        self.assertEqual(r.status_code, 404)


class JobsTest(PCEBase):
    #__test__ = False
    def setUp(self):
        super(JobsTest, self).setUp()

        testmodule_path = os.path.normpath(os.path.join(pce_root,
                                                      'src/testing/testmodule2'))
        bad_preprocess_path = os.path.normpath(os.path.join(pce_root,
                                                      'src/testing/testmodulebadpreprocess'))
        bad_postprocess_path = os.path.normpath(os.path.join(pce_root,
                                                      'src/testing/testmodulebadpostprocess'))
        good_mod_location = {
            'type': 'local',
            'path': testmodule_path
        }
        bad_preprocess_location = {
            'type': 'local',
            'path': bad_preprocess_path
        }
        bad_postprocess_location = {
            'type': 'local',
            'path': bad_postprocess_path
        }

        # Install and deploy test modules for use.
        r = pce_post('modules/', mod_id=1, mod_name='testmodule2',
                     source_location=good_mod_location)
        self.assertEqual(r.status_code, 200)
        time.sleep(3)
        r = pce_post('modules/1/')
        self.assertEqual(r.status_code, 200)
        time.sleep(3)
        r = pce_post('modules/', mod_id=2, mod_name='testmodulebadpreprocess',
                     source_location=bad_preprocess_location)
        self.assertEqual(r.status_code, 200)
        time.sleep(3)
        r = pce_post('modules/2/')
        self.assertEqual(r.status_code, 200)
        time.sleep(3)
        r = pce_post('modules/', mod_id=3, mod_name='testmodulebadpostprocess',
                     source_location=bad_postprocess_location)
        self.assertEqual(r.status_code, 200)
        time.sleep(3)
        r = pce_post('modules/3/')
        self.assertEqual(r.status_code, 200)
        time.sleep(3)

    def verify_launch(self, job_id, mod_id, username, run_name,
                      script_should_exist=True, runparams_should_exist=False):
        with JobState(job_id) as job_state:
            self.assertEqual(job_state['job_id'], job_id)
            self.assertEqual(job_state['mod_id'], mod_id)
            self.assertEqual(job_state['state'], 'Scheduled')
            self.assertEqual(job_state['username'], username)
            self.assertEqual(job_state['run_name'], run_name)
            self.assertTrue(isinstance(job_state['scheduler_job_num'], int))
            self.assertIsNone(job_state['error'])

        with ModState(mod_id) as mod_state:
            mod_name = '%s_%d' % (mod_state['mod_name'], mod_id)

        folders = (username, mod_name, run_name)
        run_dir = os.path.join(pce_root, 'users/%s/%s/%s' % folders)
        self.assertTrue(os.path.isdir(run_dir))
        script_exists = os.path.isfile(os.path.join(run_dir, 'script.sh'))
        if script_should_exist:
            self.assertTrue(script_exists)
        else:
            self.assertFalse(script_exists)
        runparams_file = os.path.join(run_dir, 'onramp_runparams.cfg')
        print runparams_file
        runparams_exists = os.path.isfile(runparams_file)
        if runparams_should_exist:
            self.assertTrue(runparams_exists)
        else:
            self.assertFalse(runparams_exists)

    def check_job(self, job, username='testuser', job_id=1, error=None,
                  state='Done', run_name='testrun1', mod_id=1):
        keys = job.keys()
        self.assertListEqual(filter(lambda x: x.startswith('_'), keys), [])
        self.assertIn('username', keys)
        self.assertIn('job_id', keys)
        self.assertIn('error', keys)
        self.assertIn('scheduler_job_num', keys)
        self.assertIn('state', keys)
        self.assertIn('run_name', keys)
        self.assertIn('mod_id', keys)
        self.assertEqual(job['username'], username)
        self.assertEqual(job['job_id'], job_id)
        self.assertEqual(job['error'], error)
        self.assertEqual(job['state'], state)
        self.assertEqual(job['run_name'], run_name)
        self.assertEqual(job['mod_id'], mod_id)

    def test_GET(self):
        # Launch a job
        r = pce_post('jobs/', mod_id=1, job_id=1, username='testuser',
                     run_name='testrun1')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], 0)
        self.assertEqual(d['status_msg'], 'Job launched')
        time.sleep(5)
        self.verify_launch(1, 1, 'testuser', 'testrun1')

        r = pce_get('jobs/1/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d, good=True)
        self.assertIn('job', d.keys())
        self.check_job(d['job'], state='Postprocessing')

        time.sleep(2)
        r = pce_get('jobs/1/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d, good=True)
        self.assertIn('job', d.keys())
        self.check_job(d['job'])

        r = pce_get('jobs/1/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d, good=True)
        self.assertIn('job', d.keys())
        self.check_job(d['job'])

        r = pce_get('jobs/')
        self.assertEqual(r.status_code, 404)

        r = pce_get('jobs/45/99/')
        self.assertEqual(r.status_code, 404)

    def test_POST(self):
        missing_msg_prefix = ('An invalid value or no value was received for the '
                              'following required parameter(s): ')

        mod_state_files = sorted(filter(lambda x: not x.startswith('.'),
                                        os.listdir(self.mod_state_dir)))
        self.assertEqual(mod_state_files, ['1', '2', '3'])
        job_state_files = filter(lambda x: not x.startswith('.'),
                                 os.listdir(self.job_state_dir))
        self.assertEqual(job_state_files, [])

        # Good post to jobs/
        r = pce_post('jobs/', mod_id=1, job_id=1, username='testuser',
                     run_name='testrun1')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], 0)
        self.assertEqual(d['status_msg'], 'Job launched')

        # Second good post to jobs/
        r = pce_post('jobs/', mod_id=1, job_id=2, username='testuser',
                     run_name='testrun2')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], 0)
        self.assertEqual(d['status_msg'], 'Job launched')

        # Verify stored state for launched jobs
        time.sleep(5)
        self.verify_launch(1, 1, 'testuser', 'testrun1')
        self.verify_launch(2, 1, 'testuser', 'testrun2')

        # Post to jobs/ with previously posted attrs
        run_dir = os.path.join(pce_root, 'users/testuser/testmodule2_1/testrun1')
        os.remove(os.path.join(run_dir, 'script.sh'))
        os.remove(os.path.join(run_dir, 'output.txt'))
        time.sleep(5)
        r = pce_post('jobs/', mod_id=1, job_id=1, username='testuser',
                     run_name='testrun1')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], 0)
        self.assertEqual(d['status_msg'], 'Job launched')

        # Verify stored state for relaunched job
        time.sleep(10)
        self.verify_launch(1, 1, 'testuser', 'testrun1',
                           script_should_exist=False)

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

        # Check output from module with preprocess error.
        r = pce_post('jobs/', mod_id=2, job_id=3, username='testuser',
                     run_name='testrunbadpreprocess')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], 0)
        self.assertEqual(d['status_msg'], 'Job launched')
        time.sleep(20)
        r = pce_get('jobs/3/')
        d = r.json()
        print d
        self.check_json(d, good=True)
        self.assertIn('job', d.keys())
        err = ("Preprocess exited with return status -1 and output: This to "
               "stderrWe're pretending this is a bad preprocess.\n")
        self.check_job(d['job'], job_id=3, state='Preprocess failed',
                       run_name='testrunbadpreprocess', mod_id=2, error=err)

        # Check output from module with postprocess error.
        r = pce_post('jobs/', mod_id=3, job_id=4, username='testuser',
                     run_name='testrunbadpostprocess')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], 0)
        self.assertEqual(d['status_msg'], 'Job launched')
        time.sleep(8)
        # Trigger postprocessing by requesting job data:
        r = pce_get('jobs/4/')
        d = r.json()
        print d
        self.check_json(d, good=True)
        self.assertIn('job', d.keys())
        self.check_job(d['job'], job_id=4, state='Postprocessing',
                       run_name='testrunbadpostprocess', mod_id=3)
        time.sleep(12)
        # Check for postprocessing failure.
        r = pce_get('jobs/4/')
        d = r.json()
        print d
        self.check_json(d, good=True)
        self.assertIn('job', d.keys())
        err = ("Postprocess exited with return status -1 and output: This to "
               "stderrWe're pretending like there was an error in this script.\n")
        self.check_job(d['job'], job_id=4, state='Postprocess failed',
                       run_name='testrunbadpostprocess', mod_id=3, error=err)

        # Check handling of cfg_params
        params = {'np': '4', 'nodes': '4', 'onramp':{}, 'hello':{'name': 'testname'}}
        r = pce_post('jobs/', mod_id=1, job_id=5, username='testuser',
                     run_name='testruncfgparams', cfg_params=params)
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], 0)
        self.assertEqual(d['status_msg'], 'Job launched')
        # Verify stored state for launched cfg_param job
        time.sleep(5)
        self.verify_launch(5, 1, 'testuser', 'testruncfgparams', runparams_should_exist=True)
        folders = ('testuser', 'testmodule2_1', 'testruncfgparams')
        run_dir = os.path.join(pce_root, 'users/%s/%s/%s' % folders)
        conf = ConfigObj(os.path.join(run_dir, 'onramp_runparams.cfg'))
        self.assertEqual(conf, params)

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

        r = pce_delete('jobs/1/1/')
        self.assertEqual(r.status_code, 404)


class ClusterTest(PCEBase):
    #__test__ = False
    def test_GET(self):
        r = pce_get('cluster/ping/')
        self.assertEqual(r.status_code, 200)

        r = pce_get('cluster/info/')
        self.assertEqual(r.status_code, 200)
        text = r.text

        r = pce_get('cluster/info/index.html')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.text, text)

        r = pce_get('cluster/info/noexist')
        self.assertEqual(r.status_code, 404)

        r = pce_get('cluster/')
        self.assertEqual(r.status_code, 404)

    def test_POST(self):
        r = pce_post('cluster/')
        self.assertEqual(r.status_code, 404)

        r = pce_post('cluster/info/')
        self.assertEqual(r.status_code, 405)

        r = pce_post('cluster/ping/')
        self.assertEqual(r.status_code, 405)

    def test_PUT(self):
        r = pce_put('cluster/')
        self.assertEqual(r.status_code, 404)

        r = pce_put('cluster/info/')
        self.assertEqual(r.status_code, 405)

        r = pce_put('cluster/ping/')
        self.assertEqual(r.status_code, 405)

    def test_DELETE(self):
        r = pce_delete('cluster/')
        self.assertEqual(r.status_code, 404)

        r = pce_delete('cluster/info/')
        self.assertEqual(r.status_code, 405)

        r = pce_delete('cluster/ping/')
        self.assertEqual(r.status_code, 405)


class ModuleJobFlowTest(PCEBase):
    #__test__ = False
    def setUp(self):
        super(ModuleJobFlowTest, self).setUp()
        self.testmodule_path = os.path.join(pce_root, 'src/testing/testmodule')

    def check_job(self, job, username='testuser', job_id=1,
                  error='Module not ready', check_scheduler_job_num=False,
                  state='Launch failed', run_name='testrun1', mod_id=1,
                  mod_status_output=None, output=None):

        keys = job.keys()
        self.assertIn('username', keys)
        self.assertIn('job_id', keys)
        self.assertIn('error', keys)
        self.assertIn('scheduler_job_num', keys)
        self.assertIn('state', keys)
        self.assertIn('run_name', keys)
        self.assertIn('mod_id', keys)
        self.assertIn('mod_status_output', keys)
        self.assertEqual(job['username'], username)
        self.assertEqual(job['job_id'], job_id)
        self.assertEqual(job['error'], error)
        self.assertEqual(job['state'], state)
        self.assertEqual(job['run_name'], run_name)
        self.assertEqual(job['mod_id'], mod_id)
        self.assertEqual(job['mod_status_output'], mod_status_output)
        self.assertEqual(job['output'], output)
        if check_scheduler_job_num:
            self.assertTrue(isinstance(job['scheduler_job_num'], int))
        else:
            self.assertIsNone(job['scheduler_job_num'])

    def check_mod(self, mod, source_location=None, installed_path=None,
                  state='Does not exist', mod_name=None, error=None, mod_id=1):

        keys = mod.keys()
        self.assertListEqual(filter(lambda x: x.startswith('_'), keys), [])
        self.assertIn('source_location', keys)
        self.assertIn('installed_path', keys)
        self.assertIn('state', keys)
        self.assertIn('mod_name', keys)
        self.assertIn('error', keys)
        self.assertIn('mod_id', keys)
        self.assertEqual(mod['source_location'], source_location)
        self.assertEqual(mod['installed_path'], installed_path)
        self.assertEqual(mod['state'], state)
        self.assertEqual(mod['mod_name'], mod_name)
        self.assertEqual(mod['error'], error)
        self.assertEqual(mod['mod_id'], mod_id)

    def test_module_job_flow(self):
        location = {
            'type': 'local',
            'path': self.testmodule_path
        }

        # Get mod that doesn't exist.
        mod_not_installed_response = pce_get('modules/1/')

        # Launch against non-existant module.
        pce_post('jobs/', mod_id=1, job_id=1, username='testuser',
               run_name='testrun1')
        time.sleep(1)
        job_no_mod_response = pce_get('jobs/1/')

        # Checkout.
        pce_post('modules/', mod_id=1, mod_name='testmodule',
               source_location=location)
        mod_installing_response = pce_get('modules/1/')

        # Launch against module currently being installed.
        pce_post('jobs/', mod_id=1, job_id=1, username='testuser',
               run_name='testrun1')
        time.sleep(1)
        job_mod_not_installed_response = pce_get('jobs/1/')

        # Let install finish.
        time.sleep(10)
        mod_installed_response = pce_get('modules/1/')

        # Launch against module installed but not deployed.
        pce_post('jobs/', mod_id=1, job_id=1, username='testuser',
               run_name='testrun1')
        time.sleep(1)
        job_mod_not_deployed_response = pce_get('jobs/1/')

        # Deploy.
        pce_post('modules/1/')
        mod_deploying_response = pce_get('modules/1/')

        # Laucnh agains module currently being deployed.
        pce_post('jobs/', mod_id=1, job_id=1, username='testuser',
               run_name='testrun1')
        time.sleep(1)
        job_mod_still_not_deployed_response = pce_get('jobs/1/')

        # Let deploy finish.
        time.sleep(15)
        mod_deployed_response = pce_get('modules/1/')

        # Launch against ready module.
        pce_post('jobs/', mod_id=1, job_id=1, username='testuser',
               run_name='testrun1')
        job_launching_response = pce_get('jobs/1/')

        # Wait a bit and check again.
        time.sleep(4)
        job_preprocessing_response = pce_get('jobs/1/')

        # Wait and check again.
        time.sleep(2)
        job_still_preprocessing_response = pce_get('jobs/1/')

        # Let preprocessing finish.
        time.sleep(8)
        job_running_response = pce_get('jobs/1/')

        # Wait a bit and check again.
        time.sleep(2)
        job_still_running_response = pce_get('jobs/1/')

        # Let job finish.
        time.sleep(8)
        job_postprocessing_response = pce_get('jobs/1/')

        # Wait a bit and check again.
        time.sleep(2)
        job_still_postprocessing_response = pce_get('jobs/1/')

        # Let postprocessing finish.
        time.sleep(10)
        job_done_response = pce_get('jobs/1/')

        # Verify contents of module log files
        run_dir = os.path.join(pce_root, 'users/testuser/testmodule_1/testrun1')
        deploy_contents_start = 'The following output was logged '
        deploy_contents_end = ('\n\nOutput to stderrmpicc -o hello -Wall -g -O0'
                               ' hello.c\nThis is an output log test.\n')
        pre_contents_start = 'The following output was logged '
        pre_contents_end = '\n\nOutput to stderrThis is an output log test.\n'
        post_contents_start = 'The following output was logged '
        post_contents_end = '\n\nOutput to stderrThis is an output log test.\n'
        status_contents_start = 'The following output was logged '
        status_contents_end = ('\n\nOutput to stderrOutput from '
                               'bin/onramp_status.py\n')
        with open(os.path.join(run_dir, 'log/onramp_deploy.log'), 'r') as f:
            contents = f.read()
            print contents
            self.assertTrue(contents.startswith(deploy_contents_start))
            self.assertTrue(contents.endswith(deploy_contents_end))
        with open(os.path.join(run_dir, 'log/onramp_preprocess.log'), 'r') as f:
            contents = f.read()
            print contents
            self.assertTrue(contents.startswith(pre_contents_start))
            self.assertTrue(contents.endswith(pre_contents_end))
        with open(os.path.join(run_dir, 'log/onramp_postprocess.log'), 'r') as f:
            contents = f.read()
            print contents
            self.assertTrue(contents.startswith(post_contents_start))
            self.assertTrue(contents.endswith(post_contents_end))
        with open(os.path.join(run_dir, 'log/onramp_status.log'), 'r') as f:
            contents = f.read()
            print contents
            self.assertTrue(contents.startswith(status_contents_start))
            self.assertTrue(contents.endswith(status_contents_end))

        print '---------------------------------'
        print 'mod_not_installed_response.text:'
        print mod_not_installed_response.text
        self.assertEqual(mod_not_installed_response.status_code, 200)
        d = mod_not_installed_response.json()
        self.check_json(d, good=True)
        self.assertIn('module', d.keys())
        self.check_mod(d['module'])

        print '---------------------------------'
        print 'job_no_mod_response.text:'
        print job_no_mod_response.text
        self.assertEqual(job_no_mod_response.status_code, 200)
        d = job_no_mod_response.json()
        self.check_json(d, good=True)
        self.assertIn('job', d.keys())
        self.check_job(d['job'])

        print '---------------------------------'
        print 'mod_installing_response.text:'
        print mod_installing_response.text
        self.assertEqual(mod_installing_response.status_code, 200)
        d = mod_installing_response.json()
        self.check_json(d, good=True)
        self.assertIn('module', d.keys())
        self.check_mod(d['module'], source_location=location,
                       state='Checkout in progress', mod_name='testmodule')

        print '---------------------------------'
        print 'job_mod_not_installed_response.text:'
        print job_mod_not_installed_response.text
        self.assertEqual(job_mod_not_installed_response.status_code, 200)
        d = job_mod_not_installed_response.json()
        self.check_json(d, good=True)
        self.assertIn('job', d.keys())
        self.check_job(d['job'])

        print '---------------------------------'
        print 'mod_installed_response.text:'
        print mod_installed_response.text
        self.assertEqual(mod_installed_response.status_code, 200)
        d = mod_installed_response.json()
        self.check_json(d, good=True)
        self.assertIn('module', d.keys())
        installed_path = os.path.join(pce_root, 'modules/testmodule_1')
        self.check_mod(d['module'], source_location=location,
                       installed_path=installed_path, mod_name='testmodule',
                       state='Installed')

        print '---------------------------------'
        print 'job_mod_not_deployed_response.text:'
        print job_mod_not_deployed_response.text
        self.assertEqual(job_mod_not_deployed_response.status_code, 200)
        d = job_mod_not_deployed_response.json()
        self.check_json(d, good=True)
        self.assertIn('job', d.keys())
        self.check_job(d['job'])

        print '---------------------------------'
        print 'mod_deploying_response.text:'
        print mod_deploying_response.text
        self.assertEqual(mod_deploying_response.status_code, 200)
        d = mod_deploying_response.json()
        self.check_json(d, good=True)
        self.assertIn('module', d.keys())
        installed_path = os.path.join(pce_root, 'modules/testmodule_1')
        self.check_mod(d['module'], source_location=location,
                       installed_path=installed_path, mod_name='testmodule',
                       state='Deploy in progress')

        print '---------------------------------'
        print 'job_mod_still_not_deployed_response.text:'
        print job_mod_still_not_deployed_response.text
        self.assertEqual(job_mod_still_not_deployed_response.status_code, 200)
        d = job_mod_still_not_deployed_response.json()
        self.check_json(d, good=True)
        self.assertIn('job', d.keys())
        self.check_job(d['job'])

        print '---------------------------------'
        print 'mod_deployed_response.text:'
        print mod_deployed_response.text
        self.assertEqual(mod_deployed_response.status_code, 200)
        d = mod_deployed_response.json()
        self.check_json(d, good=True)
        self.assertIn('module', d.keys())
        installed_path = os.path.join(pce_root, 'modules/testmodule_1')
        self.check_mod(d['module'], source_location=location,
                       installed_path=installed_path, mod_name='testmodule',
                       state='Module ready')

        print '---------------------------------'
        print 'job_launching_response.text:'
        print job_launching_response.text
        self.assertEqual(job_launching_response.status_code, 200)
        d = job_launching_response.json()
        self.check_json(d, good=True)
        self.assertIn('job', d.keys())
        self.check_job(d['job'], state='Setting up launch', error=None)

        print '---------------------------------'
        print 'job_preprocessing_response.text:'
        print job_preprocessing_response.text
        self.assertEqual(job_preprocessing_response.status_code, 200)
        d = job_preprocessing_response.json()
        self.check_json(d, good=True)
        self.assertIn('job', d.keys())
        self.check_job(d['job'], state='Preprocessing', error=None)

        print '---------------------------------'
        print 'job_still_preprocessing_response.text:'
        print job_still_preprocessing_response.text
        self.assertEqual(job_still_preprocessing_response.status_code, 200)
        d = job_still_preprocessing_response.json()
        self.check_json(d, good=True)
        self.assertIn('job', d.keys())
        self.check_job(d['job'], state='Preprocessing', error=None)

        print '---------------------------------'
        print 'job_running_response.text:'
        print job_running_response.text
        self.assertEqual(job_running_response.status_code, 200)
        d = job_running_response.json()
        self.check_json(d, good=True)
        self.assertIn('job', d.keys())
        output = 'Output to stderrOutput from bin/onramp_status.py\n'
        self.check_job(d['job'], state='Running', check_scheduler_job_num=True,
                       error=None, mod_status_output=output)

        print '---------------------------------'
        print 'job_still_running_response.text:'
        print job_still_running_response.text
        self.assertEqual(job_still_running_response.status_code, 200)
        d = job_still_running_response.json()
        self.check_json(d, good=True)
        self.assertIn('job', d.keys())
        output = 'Output to stderrOutput from bin/onramp_status.py\n'
        self.check_job(d['job'], state='Running', check_scheduler_job_num=True,
                       error=None, mod_status_output=output)

        print '---------------------------------'
        print 'job_postprocessing_response.text:'
        print job_postprocessing_response.text
        self.assertEqual(job_postprocessing_response.status_code, 200)
        d = job_postprocessing_response.json()
        self.check_json(d, good=True)
        self.assertIn('job', d.keys())
        self.check_job(d['job'], state='Postprocessing',
                       check_scheduler_job_num=True, error=None)

        print '---------------------------------'
        print 'job_still_postprocessing_response.text:'
        print job_still_postprocessing_response.text
        self.assertEqual(job_postprocessing_response.status_code, 200)
        d = job_still_postprocessing_response.json()
        self.check_json(d, good=True)
        self.assertIn('job', d.keys())
        self.check_job(d['job'], state='Postprocessing',
                       check_scheduler_job_num=True, error=None)

        print '---------------------------------'
        print 'job_done_response.text:'
        print job_done_response.text
        self.assertEqual(job_done_response.status_code, 200)
        d = job_done_response.json()
        self.check_json(d, good=True)
        self.assertIn('job', d.keys())
        output = ('Hello, this will result in deterministic output!Hello, this '
                  'will result in deterministic output!Hello, this will result '
                  'in deterministic output!Hello, this will result in '
                  'deterministic output!')
        self.check_job(d['job'], state='Done',
                       check_scheduler_job_num=True, error=None, output=output)
        self.assertIn('visible_files', d['job'].keys())
        visible_files = d['job']['visible_files']
        self.assertEqual(len(visible_files), 3)
        names = []
        for f in visible_files:
            keys = f.keys()
            self.assertIn('name', keys)
            self.assertIn('size', keys)
            self.assertIn('url', keys)
            self.assertTrue(f['url'].endswith(f['name']))
            names.append(f['name'])
        self.assertIn('output.txt', names)
        self.assertIn('script.sh', names)
        self.assertIn('bin/onramp_status.py', names)
        
        r = pce_get('files/testuser/testmodule_1/testrun1/output.txt')
        self.assertEqual(r.status_code, 200)
        fname = os.path.join(pce_root,
                             'users/testuser/testmodule_1/testrun1/output.txt')
        with open(fname) as f:
            self.assertEqual(r.text, f.read())

        r = pce_get('files/testuser/testmodule_1/testrun1/onramp_runparams.cfg')
        self.assertEqual(r.status_code, 403)
        self.assertEqual(r.text, 'Requested file not configured to be visible')

        r = pce_get('files/testuser/testmodule_1/testrun1/script.sh')
        self.assertEqual(r.status_code, 200)
        fname = os.path.join(pce_root,
                             'users/testuser/testmodule_1/testrun1/script.sh')
        with open(fname) as f:
            self.assertEqual(r.text, f.read())

        r = pce_get('files/testuser/testmodule_1/testrun1/bin/onramp_status.py')
        self.assertEqual(r.status_code, 200)
        fname = os.path.join(pce_root,
                             ('users/testuser/testmodule_1/'
                              'testrun1/bin/onramp_status.py'))
        with open(fname) as f:
            self.assertEqual(r.text, f.read())

        r = pce_get('files/testuser/testmodule_1/testrun1/')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.text, 'Bad request')

        r = pce_get('files/testuser/testmodule_1/')
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.text, 'Bad request')

    def test_mod_delete(self):
        location = {
            'type': 'local',
            'path': self.testmodule_path
        }

        state_file = os.path.join(pce_root, 'src/state/modules/1')
        installed_path = os.path.join(pce_root, 'modules/testmodule_1')

        def checkout(sleep_time=5):
            pce_post('modules/', mod_id=1, mod_name='testmodule',
                   source_location=location)
            time.sleep(sleep_time)
            r = pce_get('modules/1/')
            self.assertEqual(r.status_code, 200)
            d = r.json()
            self.check_json(d, good=True)
            self.assertIn('module', d.keys())
            self.assertIn('state', d['module'].keys())
            if sleep_time == 0:
                self.assertEqual(d['module']['state'], 'Checkout in progress')
            else:
                self.assertEqual(d['module']['state'], 'Installed')
                self.assertIn('installed_path', d['module'].keys())
                self.assertEqual(d['module']['installed_path'], installed_path)
                self.assertTrue(os.path.exists(installed_path))
            self.assertTrue(os.path.exists(state_file))

        def delete(immediate=True):
            r = pce_delete('modules/1/')
            self.assertEqual(r.status_code, 200)
            if immediate:
                self.assertFalse(os.path.exists(state_file))
                self.assertFalse(os.path.exists(installed_path))

        def deploy():
            r = pce_post('modules/1/')
            self.assertEqual(r.status_code, 200)
            r = pce_get('modules/1/')
            self.assertEqual(r.status_code, 200)
            d = r.json()
            self.check_json(d, good=True)
            self.assertIn('module', d.keys())
            self.assertIn('state', d['module'].keys())
            self.assertEqual(d['module']['state'], 'Deploy in progress')

        # Test delete of non-existat module.
        r = pce_delete('modules/1/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d)
        self.assertEqual(d['status_code'], 0)
        self.assertEqual(d['status_msg'], 'Module 1 not currently installed')

        # Check delete during install.
        checkout(sleep_time=0)
        delete(immediate=False)
        time.sleep(3)
        self.assertFalse(os.path.exists(state_file))
        self.assertFalse(os.path.exists(installed_path))

        # Check delete after install.
        checkout()
        delete()

        # Check delete while deploy in progress.
        checkout()
        deploy()
        delete(immediate=False)
        time.sleep(5)
        self.assertTrue(os.path.exists(state_file))
        self.assertTrue(os.path.exists(installed_path))
        time.sleep(6)
        self.assertFalse(os.path.exists(state_file))
        self.assertFalse(os.path.exists(installed_path))

        # Check delete while deploy in progress with deploy failure.
        source = os.path.join(installed_path, 'bin/onramp_deploy_bad.py')
        dest = os.path.join(installed_path, 'bin/onramp_deploy.py')
        checkout()
        shutil.copyfile(source, dest)
        deploy()
        delete(immediate=False)
        time.sleep(5)
        self.assertTrue(os.path.exists(state_file))
        self.assertTrue(os.path.exists(installed_path))
        time.sleep(6)
        self.assertFalse(os.path.exists(state_file))
        self.assertFalse(os.path.exists(installed_path))

        # Check delete while deploy in progress with admin required.
        source = os.path.join(installed_path, 'bin/onramp_deploy_admin.py')
        dest = os.path.join(installed_path, 'bin/onramp_deploy.py')
        checkout()
        shutil.copyfile(source, dest)
        deploy()
        delete(immediate=False)
        time.sleep(5)
        self.assertTrue(os.path.exists(state_file))
        self.assertTrue(os.path.exists(installed_path))
        time.sleep(6)
        self.assertFalse(os.path.exists(state_file))
        self.assertFalse(os.path.exists(installed_path))

        # Check delete while module ready.
        checkout()
        deploy()
        time.sleep(11)
        delete()

    def test_job_delete(self):
        location = {
            'type': 'local',
            'path': self.testmodule_path
        }

        mod_state_file = os.path.join(pce_root, 'src/state/modules/1')
        mod_installed_path = os.path.join(pce_root, 'modules/testmodule_1')
        job_state_file = os.path.join(pce_root, 'src/state/jobs/1')
        run_dir = os.path.join(pce_root, 'users/testuser/testmodule_1/testrun')
        mod_dir = os.path.join(pce_root, 'modules/testmodule_1')

        def checkout(sleep_time=5):
            pce_post('modules/', mod_id=1, mod_name='testmodule',
                   source_location=location)
            time.sleep(sleep_time)
            r = pce_get('modules/1/')
            self.assertEqual(r.status_code, 200)
            d = r.json()
            self.check_json(d, good=True)
            self.assertIn('module', d.keys())
            self.assertIn('state', d['module'].keys())
            if sleep_time == 0:
                self.assertEqual(d['module']['state'], 'Checkout in progress')
            else:
                self.assertEqual(d['module']['state'], 'Installed')
                self.assertIn('installed_path', d['module'].keys())
                self.assertEqual(d['module']['installed_path'], mod_installed_path)
                self.assertTrue(os.path.exists(mod_installed_path))
            self.assertTrue(os.path.exists(mod_state_file))

        def deploy():
            r = pce_post('modules/1/')
            self.assertEqual(r.status_code, 200)
            r = pce_get('modules/1/')
            self.assertEqual(r.status_code, 200)
            d = r.json()
            self.check_json(d, good=True)
            self.assertIn('module', d.keys())
            self.assertIn('state', d['module'].keys())
            self.assertEqual(d['module']['state'], 'Deploy in progress')

        def launch():
            pce_post('jobs/', mod_id=1, job_id=1, username='testuser',
                     run_name='testrun')

        def delete(immediate=True):
            r = pce_delete('jobs/1/')
            print r.text
            self.assertEqual(r.status_code, 200)
            if immediate:
                self.assertFalse(os.path.exists(job_state_file))
                self.assertFalse(os.path.exists(run_dir))
            else:
                self.assertTrue(os.path.exists(job_state_file))

        # Setup testmodule.
        checkout()

        # Non-existant.
        delete()

        # Setting up launch -> Launch failed (module not ready).
        launch()
        delete()
        
        # Launch failed.
        launch()
        time.sleep(5)
        delete()

        # Setting up launch -> Scheduled.
        time.sleep(5)
        deploy()
        time.sleep(11)
        launch()
        delete(immediate=False)
        time.sleep(13)
        self.assertFalse(os.path.exists(job_state_file))
        self.assertFalse(os.path.exists(run_dir))
        
        # Setting up launch -> Preprocess failed.
        time.sleep(5)
        source = os.path.join(mod_dir, 'bin/onramp_preprocess_bad.py')
        dest = os.path.join(mod_dir, 'bin/onramp_preprocess.py')
        shutil.copyfile(source, dest)
        launch()
        delete(immediate=False)
        time.sleep(14)
        self.assertFalse(os.path.exists(job_state_file))
        self.assertFalse(os.path.exists(run_dir))

        # Preprocessing -> Preprocess failed.
        time.sleep(5)
        launch()
        time.sleep(7)
        delete(immediate=False)
        time.sleep(8)
        self.assertFalse(os.path.exists(job_state_file))
        self.assertFalse(os.path.exists(run_dir))

        # Preprocessing -> Scheduled.
        time.sleep(5)
        source = os.path.join(mod_dir, 'bin/onramp_preprocess_good.py')
        dest = os.path.join(mod_dir, 'bin/onramp_preprocess.py')
        shutil.copyfile(source, dest)
        launch()
        time.sleep(7)
        delete(immediate=False)
        time.sleep(7)
        self.assertFalse(os.path.exists(job_state_file))
        self.assertFalse(os.path.exists(run_dir))

        # Preprocess failed.
        time.sleep(5)
        source = os.path.join(mod_dir, 'bin/onramp_preprocess_bad.py')
        dest = os.path.join(mod_dir, 'bin/onramp_preprocess.py')
        shutil.copyfile(source, dest)
        launch()
        time.sleep(15)
        delete()

        # Scheduled/Queued/Running.
        time.sleep(5)
        source = os.path.join(mod_dir, 'bin/onramp_preprocess_good.py')
        dest = os.path.join(mod_dir, 'bin/onramp_preprocess.py')
        shutil.copyfile(source, dest)
        launch()
        time.sleep(15)
        delete()

        # Running.
        time.sleep(20)
        launch()
        time.sleep(20)
        r = pce_get('jobs/1/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d, good=True)
        self.assertIn('job', d.keys())
        self.assertIn('state', d['job'].keys())
        self.assertEqual(d['job']['state'], 'Running')
        delete()

        # Postprocessing -> Done.
        time.sleep(20)
        launch()
        time.sleep(30)
        r = pce_get('jobs/1/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d, good=True)
        self.assertIn('job', d.keys())
        self.assertIn('state', d['job'].keys())
        self.assertEqual(d['job']['state'], 'Postprocessing')
        delete(immediate=False)
        time.sleep(12)
        self.assertFalse(os.path.exists(job_state_file))
        self.assertFalse(os.path.exists(run_dir))

        # Postprocessing -> Postprocess failed.
        source = os.path.join(mod_dir, 'bin/onramp_postprocess_bad.py')
        dest = os.path.join(mod_dir, 'bin/onramp_postprocess.py')
        shutil.copyfile(source, dest)
        time.sleep(20)
        launch()
        time.sleep(30)
        r = pce_get('jobs/1/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d, good=True)
        self.assertIn('job', d.keys())
        self.assertIn('state', d['job'].keys())
        self.assertEqual(d['job']['state'], 'Postprocessing')
        delete(immediate=False)
        time.sleep(12)
        self.assertFalse(os.path.exists(job_state_file))
        self.assertFalse(os.path.exists(run_dir))

        # Postprocess failed.
        time.sleep(20)
        launch()
        time.sleep(30)
        r = pce_get('jobs/1/')
        time.sleep(15)
        r = pce_get('jobs/1/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d, good=True)
        self.assertIn('job', d.keys())
        self.assertIn('state', d['job'].keys())
        self.assertEqual(d['job']['state'], 'Postprocess failed')
        delete()

        # Done
        time.sleep(20)
        source = os.path.join(mod_dir, 'bin/onramp_postprocess_good.py')
        dest = os.path.join(mod_dir, 'bin/onramp_postprocess.py')
        shutil.copyfile(source, dest)
        launch()
        time.sleep(30)
        r = pce_get('jobs/1/')
        time.sleep(15)
        r = pce_get('jobs/1/')
        self.assertEqual(r.status_code, 200)
        d = r.json()
        self.check_json(d, good=True)
        self.assertIn('job', d.keys())
        self.assertIn('state', d['job'].keys())
        self.assertEqual(d['job']['state'], 'Done')
        delete()

        # TODO: 
        # Setting up launch -> Launch failed (runparams validation failed).
        # Setting up launch -> Launch failed (project location does not exist).
