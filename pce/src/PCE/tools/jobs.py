"""OnRamp job launching support package.

Provides functionality for launching jobs, as well as means of
setting/storing/updating job state data.

Exports:
    JobState: Encapsulation of job state that avoids race conditions.
    launch_job: Schedules job launch using system batch scheduler as configured
        in onramp_pce_config.ini.
    get_jobs: Returns list of tracked jobs or single job.
"""
import argparse
import copy
import errno
import fcntl
import json
import logging
import os
import shutil
import sys
from multiprocessing import Process
from subprocess import CalledProcessError, check_output

from configobj import ConfigObj
from validate import Validator

from PCE import pce_root
from PCE.tools.modules import ModState
from PCE.tools.schedulers import Scheduler

_job_state_dir = os.path.join(pce_root, 'src/state/jobs')
_mod_install_dir = os.path.join(pce_root, 'modules')
_logger = logging.getLogger('onramp')

class JobState(dict):
    """Provide access to job state in a way that race conditions are avoided.

    JobState() is only intended to be used in combination with the 'with' python
    keyword. State parameters are stored/acessed as dict keys.
    
    Example:

        with JobState(47) as job_state:
            val = job_state['key1']
            job_state['key2'] = 'val2'
    """

    def __init__(self, id):
        """Return initialized JobState instance.

        Method works in get-or-create fashion, that is, if state exists for
        job id, open and return it, else create and return it.

        Args:
            id (int): Id of the job to get/create state for.
        """
        job_state_file = os.path.join(_job_state_dir, str(id))

        try:
            # Raises OSError if file cannot be opened in create mode. If no
            # error, lock the file descriptor when opened.
            fd = os.open(job_state_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            fcntl.flock(fd, fcntl.LOCK_EX)
            self._state_file = os.fdopen(fd, 'w')
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
            # File already exists. Open and lock it.
            self._state_file = open(job_state_file, 'r+')
            fcntl.lockf(self._state_file, fcntl.LOCK_EX)
            self.update(json.loads(self._state_file.read()))
            self._state_file.seek(0)

    def __enter__(self):
        """Provide entry for use in 'with' statements."""
        return self

    def __exit__(self, type, value, traceback):
        """Provide exit for use in 'with' statements."""
        self._close()

    def _close(self):
        """Serialize and store state parameters.

        If stored state exists, overwrite it with current instance keys/vals.
        """
        if 'state' in self.keys() and self['state'] != 'Does not exist':
            self._state_file.write(json.dumps(self))
            self._state_file.truncate()
        self._state_file.close()


def launch_job(job_id, mod_id, username, run_name):
    """Schedule job launch using system batch scheduler as configured in
    onramp_pce_config.ini.

    Args:
        job_id (int): Unique identifier for job.
        mod_id (int): Id for OnRamp educational module to run in this job.
        username (str): Username of user running the job.
        run_name (str): Human-readable label for this job run.
    """
    accepted_states = ['Schedule failed', 'Launch failed', 'Preprocess failed']
    _logger.debug('PCE.tools.launch_job() called')

    # Initialize job state.
    with JobState(job_id) as job_state:
        if ('state' in job_state.keys()
            and job_state['state'] not in accepted_states):
            return (-1, 'Job launch already initiated')

        job_state['job_id'] = job_id
        job_state['mod_id'] = mod_id
        job_state['username'] = username
        job_state['scheduler_job_num'] = None
        job_state['state'] = 'Setting up launch'
        job_state['error'] = None

    # Get module attrs.
    with ModState(mod_id) as mod_state:
        if ('state' not in mod_state.keys()
            or mod_state['state'] != 'Module ready'):
            with JobState(job_id) as job_state:
                job_state['state'] = 'Launch failed'
                job_state['error'] = 'Module not ready'
            return (-1, 'Module not ready')
        proj_loc = mod_state['installed_path']
        mod_name = mod_state['mod_name']

    if not os.path.isdir(proj_loc):
        msg = 'Project location does not exist'
        _logger.error(msg)
        return (-1, msg)

    # Initialize dir structure.
    user_dir = os.path.join(os.path.join(pce_root, 'users'), username)
    if not os.path.isdir(user_dir):
        os.mkdir(user_dir)
    user_mod_dir = os.path.join(user_dir, '%s_%s' % (mod_name, mod_id))
    if not os.path.isdir(user_mod_dir):
        os.mkdir(user_mod_dir)
    run_dir = os.path.join(user_mod_dir, run_name)
    if not os.path.isdir(run_dir):
        shutil.copytree(proj_loc, run_dir)

    ret_dir = os.getcwd()
    os.chdir(run_dir)

    # Preprocess.
    _logger.info('Calling bin/onramp_preprocess.py')
    with JobState(job_id) as job_state:
        job_state['state'] = 'Preprocessing'
        job_state['error'] = None

    try:
        result = check_output([os.path.join(pce_root, 'src/env/bin/python'),
                               'bin/onramp_preprocess.py'])
    except CalledProcessError as e:
        msg = 'Preprocess failed'
        with JobState(job_id) as job_state:
            job_state['state'] = msg
            job_state['error'] = 'Return status: %d' % e.output
        _logger.error(msg)
        os.chdir(ret_dir)
        return (-1, msg)

    # Determine batch scheduler to user from config.
    ini = ConfigObj(os.path.join(pce_root, 'onramp_pce_config.ini'),
                    configspec=os.path.join(pce_root,
                                            'src/onramp_config.inispec'))
    ini.validate(Validator())
    scheduler = Scheduler(ini['cluster']['batch_scheduler'])

    # Write batch script.
    with open('script.sh', 'w') as f:
        args =(username, mod_name, mod_id, job_id)
        f.write(scheduler.get_batch_script(run_name))

    # Schedule job.
    result = scheduler.schedule(run_dir)
    if result['status_code'] != 0:
        _logger.error(result['msg'])
        with JobState(job_id) as job_state:
            job_state['state'] = 'Schedule failed'
            job_state['error'] = result['msg']
        os.chdir(ret_dir)
        return (result['returncode'], result['msg'])
    
    with JobState(job_id) as job_state:
        job_state['state'] = 'Scheduled'
        job_state['error'] = None
        job_state['scheduler_job_num'] = result['job_num']

    os.chdir(ret_dir)
    return (0, 'Job scheduled')

def get_jobs(job_id=None):
    """Return list of tracked jobs or single job.

    Kwargs:
        job_id (int/None): If int, return jobs resource with corresponding id.
            If None, return list of all tracked job resources.
    """
    if job_id:
        with JobState(job_id) as job_state:
            if 'state' in job_state.keys():
                return copy.deepcopy(job_state)
        return {
            'job_id': job_id,
            'mod_id': None,
            'state': 'Does not exist',
            'error': None
        }

    results = []
    for id in os.listdir(_job_state_dir):
        next_job = {}
        with JobState(id) as job_state:
            next_job = copy.deepcopy(job_state)
        results.append(next_job)
    return results
