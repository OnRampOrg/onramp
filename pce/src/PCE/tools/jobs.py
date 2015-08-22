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
import time
from multiprocessing import Process
from subprocess import CalledProcessError, call, check_output

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
            file_contents = self._state_file.read()
            _logger.debug('File contents for %s:' % job_state_file)
            _logger.debug(file_contents)

            try:
                data = json.loads(file_contents)
                # Valid json. Load it into self.
                self.update(data)
            except ValueError:
                # Invalid json. Ignore (will be overwritten by _close().
                pass

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
            msg = 'Job launch already initiated'
            _logger.warn(msg)
            return (-1, msg)

        job_state['job_id'] = job_id
        job_state['mod_id'] = mod_id
        job_state['username'] = username
        job_state['run_name'] = run_name
        job_state['scheduler_job_num'] = None
        job_state['state'] = 'Setting up launch'
        job_state['error'] = None
        job_state['mod_status_output'] = None
        job_state['output'] = None
        _logger.debug('Waiting on ModState at: %s' % time.time())
        with ModState(mod_id) as mod_state:
            _logger.debug('Done waiting on ModState at: %s' % time.time())
            if ('state' not in mod_state.keys()
                or mod_state['state'] != 'Module ready'):
                msg = 'Module not ready'
                job_state['state'] = 'Launch failed'
                job_state['error'] = msg
                _logger.warn(msg)
                _logger.warn('mod_state: %s' % str(mod_state))
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
    user_mod_dir = os.path.join(user_dir, '%s_%d' % (mod_name, mod_id))
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

def _job_postprocess(job_id):
    """Run bin/onramp_postprocess.py for job_id and update state to reflect.

    Args:
        job_id (int): Id of the job to launch bin/onramp_postprocess.py for.
    """
    _logger.info('PCE.tools.jobs._job_postprocess() called')

    # Get attrs needed.
    with JobState(job_id) as job_state:
        username = job_state['username']
        mod_id = job_state['mod_id']
        run_name = job_state['run_name']
    with ModState(mod_id) as mod_state:
        mod_name = mod_state['mod_name']
    args = (username, mod_name, mod_id, run_name)
    run_dir = os.path.join(pce_root, 'users/%s/%s_%d/%s' % args)
    ret_dir = os.getcwd()

    os.chdir(run_dir)
    _logger.debug('Calling bin/onramp_postprocess.py')
    call([os.path.join(pce_root, 'src/env/bin/python'),
          'bin/onramp_postprocess.py'])

    # Grab job output.
    with open('output.txt', 'r') as f:
        output = f.read()
    os.chdir(ret_dir)

    # Update state.
    with JobState(job_id) as job_state:
        job_state['state'] = 'Done'
        job_state['error'] = None
        job_state['output'] = output

def _get_module_status_output(job_id):
    """Run bin/onramp_status.py for job and return any output.

    Args:
        job_id (int): Id of the job to launch bin/onramp_status.py for.
    """
    # Get attrs needed.
    with JobState(job_id) as job_state:
        username = job_state['username']
        mod_id = job_state['mod_id']
        run_name = job_state['run_name']
    with ModState(mod_id) as mod_state:
        mod_name = mod_state['mod_name']
    args = (username, mod_name, mod_id, run_name)
    run_dir = os.path.join(pce_root, 'users/%s/%s_%d/%s' % args)
    ret_dir = os.getcwd()

    # Run bin/onramp_status.py and grab output.
    os.chdir(run_dir)
    _logger.debug('Calling bin/onramp_status.py')
    try:
        output = check_output([os.path.join(pce_root, 'src/env/bin/python'),
                               'bin/onramp_status.py'])
    except CalledProcessError as e:
        output = 'bin/onramp_status.py exited with nonzero status.'
    finally:
        os.chdir(ret_dir)

    return output

def _build_job(job_id):
    """Launch actions required to maintain job state and/or currate job results
    and return the state.

    When current job state (as a function of both PCE state tracking and
    scheduler output) warrants, initiate job postprocessing and/or status
    checking prior to building and returning state.

    Args:
        job_id (int): Id of the job to get state for.
    """
    status_check_states = ['Scheduled', 'Queued', 'Running']
    with JobState(job_id) as job_state:
        _logger.debug('Building at %s' % time.time())
        if 'state' not in job_state.keys():
            _logger.debug('No state at %s' % time.time())
            _logger.debug('job_state keys: %s' % job_state.keys())
            return {}

        if job_state['state'] in status_check_states:
            ini = ConfigObj(os.path.join(pce_root, 'onramp_pce_config.ini'),
                            configspec=os.path.join(pce_root,
                                                'src/onramp_config.inispec'))
            ini.validate(Validator())
            scheduler = Scheduler(ini['cluster']['batch_scheduler'])
            sched_job_num = job_state['scheduler_job_num']
            job_status = scheduler.check_status(sched_job_num)

            # Bad.
            if job_status[0] != 0:
                _logger.debug('Bad job status: %s' % job_status[1])
                job_state['state'] = 'Run failed'
                job_state['error'] = job_status[1]
                if job_status != -2:
                    job_state['state'] = job_status[1]
                return copy.deepcopy(job_state)

            # Good.
            if job_status[1] == 'Done':
                job_state['state'] = 'Postprocessing'
                job_state['error'] = None
                job_state['mod_status_output'] = None
                p = Process(target=_job_postprocess, args=(job_id,))
                p.start()
            elif job_status[1] == 'Running':
                job_state['state'] = 'Running'
                job_state['error'] = None
                mod_status_output = _get_module_status_output(job_id)
                job_state['mod_status_output'] = mod_status_output
            elif job_status[1] == 'Queued':
                job_state['state'] = 'Queued'
                job_state['error'] = None

        return copy.deepcopy(job_state)

def get_jobs(job_id=None):
    """Return list of tracked jobs or single job.

    Kwargs:
        job_id (int/None): If int, return jobs resource with corresponding id.
            If None, return list of all tracked job resources.
    """
    if job_id:
        return _build_job(job_id)

    return [_build_job(job_id) for job_id in
            filter(lambda x: not x.startswith('.'),
                   os.listdir(_job_state_dir))]
