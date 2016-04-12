"""OnRamp job launching support package.

Provides functionality for launching jobs, as well as means of
setting/storing/updating job state data.

Exports:
    JobState: Encapsulation of job state that avoids race conditions.
    launch_job: Schedules job launch using system batch scheduler as configured
        in onramp_pce_config.cfg.
    get_jobs: Returns list of tracked jobs or single job.
    init_job_delete: Initiate the deletion of a job.
"""
import argparse
import copy
import errno
import fcntl
import json
import glob
import logging
import os
import shutil
import sys
import time
from itertools import chain
from multiprocessing import Process
from subprocess import CalledProcessError, call, check_output, STDOUT

from configobj import ConfigObj
from validate import Validator

from PCE.tools import module_log
from PCE.tools.modules import ModState
from PCE.tools.schedulers import Scheduler
from PCEHelper import pce_root

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

    def __init__(self, id, job_state_file=None):
        """Return initialized JobState instance.

        Method works in get-or-create fashion, that is, if state exists for
        job id, open and return it, else create and return it.

        Args:
            id (int): Id of the job to get/create state for.
        """
        if job_state_file is None:
            job_state_file = os.path.join(_job_state_dir, str(id))
        self.job_id = id

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
        else:
            job_state_file = os.path.join(_job_state_dir, str(self.job_id))
            try:
                os.remove(job_state_file)
            except OSError as e:
                if e.errno != 2:
                    # 2 => No such file or directory (which is no prob).
                    raise e
        self._state_file.close()

def launch_job(job_id, mod_id, username, run_name, run_params):
    """Schedule job launch using system batch scheduler as configured in
    onramp_pce_config.cfg.

    Args:
        job_id (int): Unique identifier for job.
        mod_id (int): Id for OnRamp educational module to run in this job.
        username (str): Username of user running the job.
        run_name (str): Human-readable label for this job run.

    Returns:
        Tuple with 0th position being error code and 1st position being string
        indication of status.
    """
    accepted_states = ['Schedule failed', 'Launch failed', 'Preprocess failed']
    _logger.debug('PCE.tools.launch_job() called')

    # Initialize job state.
    with JobState(job_id) as job_state:
        if ('state' in job_state.keys()
            and job_state['state'] not in accepted_states):
            msg = ('Job launch already initiated. '
                   'Has state %s.' % job_state['state'])
            _logger.warn(msg)
            return (-1, msg)

    ret = job_init_state(job_id, mod_id, username, run_name, run_params)
    if ret[0] != 0:
        return ret
    ret = job_preprocess(job_id)
    if ret[0] != 0:
        return ret
    return job_run(job_id)

def job_init_state(job_id, mod_id, username, run_name, run_params,
                   job_state_file=None, mod_state_file=None,
                   run_dir=None):

    with JobState(job_id, job_state_file) as job_state:
        job_state['job_id'] = job_id
        job_state['mod_id'] = mod_id
        job_state['username'] = username
        job_state['run_name'] = run_name
        job_state['scheduler_job_num'] = None
        job_state['state'] = 'Setting up launch'
        job_state['error'] = None
        job_state['mod_status_output'] = None
        job_state['output'] = None
        job_state['visible_files'] = None
        job_state['mod_name'] = None
        job_state['_marked_for_del'] = False
        _logger.debug('Waiting on ModState at: %s' % time.time())
        with ModState(mod_id, mod_state_file) as mod_state:
            _logger.debug('Done waiting on ModState at: %s' % time.time())
            if ('state' not in mod_state.keys()
                or mod_state['state'] != 'Module ready'):
                msg = 'Module not ready'
                job_state['state'] = 'Launch failed'
                job_state['error'] = msg
                _logger.warn(msg)
                _logger.warn('mod_state: %s' % str(mod_state))
                if job_state['_marked_for_del']:
                    _delete_job(job_state)
                    return (-2, 'Job %d deleted' % job_id)
                return (-1, 'Module not ready')
            job_state['mod_name'] = mod_state['mod_name']
            proj_loc = mod_state['installed_path']
            mod_name = mod_state['mod_name']

    _logger.debug('Testing project location')
    if not os.path.isdir(proj_loc):
        msg = 'Project location does not exist'
        _logger.error(msg)
        return (-1, msg)
    _logger.debug('Project location good')

    # Initialize dir structure.
    if run_dir is None:
        user_dir = os.path.join(os.path.join(pce_root, 'users'), username)
        user_mod_dir = os.path.join(user_dir, '%s_%d' % (mod_name, mod_id))
        run_dir = os.path.join(user_mod_dir, run_name)
        try:
            os.mkdir(user_dir)
        except OSError:
            # Thrown if dir already exists.
            pass
        try:
            os.mkdir(user_mod_dir)
        except OSError:
            # Thrown if dir already exists.
            pass

    with JobState(job_id, job_state_file) as job_state:
        job_state['run_dir'] = run_dir

    # The way the following is setup, if a run_dir has already been setup with
    # this run_name, it will be used (that is, not overwritten) for this launch.
    try:
        shutil.copytree(proj_loc, run_dir)
    except (shutil.Error, OSError) as e:
        pass
    if run_params:
        _logger.debug('Handling run_params')
        spec = os.path.join(run_dir, 'config/onramp_uioptions.cfgspec')
        params = ConfigObj(run_params, configspec=spec)
        result = params.validate(Validator())
        if result:
            with open(os.path.join(run_dir, 'onramp_runparams.cfg'), 'w') as f:
                params.write(f)
        else:
            msg = 'Runparams failed validation'
            _logger.warn(msg)
            return (-1, msg)

    return (0, 'Job state initialized')


def job_preprocess(job_id, job_state_file=None):
    ret_dir = os.getcwd()
    _logger.info('Calling bin/onramp_preprocess.py')
    with JobState(job_id, job_state_file) as job_state:
        job_state['state'] = 'Preprocessing'
        job_state['error'] = None
        run_dir = job_state['run_dir']
    os.chdir(run_dir)

    try:
        result = check_output([os.path.join(pce_root, 'src/env/bin/python'),
                               'bin/onramp_preprocess.py'], stderr=STDOUT)
    except CalledProcessError as e:
        code = e.returncode
        if code > 127:
            code -= 256
        result = e.output
        msg = ('Preprocess exited with return status %d and output: %s'
               % (code, result))
        with JobState(job_id, job_state_file) as job_state:
            job_state['state'] = 'Preprocess failed'
            job_state['error'] = msg
            _logger.error(msg)
            if job_state['_marked_for_del']:
                _delete_job(job_state)
                return (-2, 'Job %d deleted' % job_id)
        return (-1, msg)
    finally:
        module_log(run_dir, 'preprocess', result)
        os.chdir(ret_dir)

    return (0, 'Job preprocess complete')

def job_run(job_id, job_state_file=None):
    # Determine batch scheduler to user from config.
    cfg = ConfigObj(os.path.join(pce_root, 'bin', 'onramp_pce_config.cfg'),
                    configspec=os.path.join(pce_root, 'src', 'configspecs',
                                            'onramp_pce_config.cfgspec'))
    cfg.validate(Validator())
    scheduler = Scheduler(cfg['cluster']['batch_scheduler'])

    ret_dir = os.getcwd()
    with JobState(job_id, job_state_file) as job_state:
        run_dir = job_state['run_dir']
        run_name = job_state['run_name']
    os.chdir(run_dir)

    # Write batch script.
    with open('script.sh', 'w') as f:
        f.write(scheduler.get_batch_script(run_name))

    # Schedule job.
    result = scheduler.schedule(run_dir)

    if result['status_code'] != 0:
        _logger.error(result['msg'])
        with JobState(job_id, job_state_file) as job_state:
            job_state['state'] = 'Schedule failed'
            job_state['error'] = result['msg']
            os.chdir(ret_dir)
            if job_state['_marked_for_del']:
                _delete_job(job_state)
                return (-2, 'Job %d deleted' % job_id)
        return (result['returncode'], result['msg'])
    
    with JobState(job_id, job_state_file) as job_state:
        job_state['state'] = 'Scheduled'
        job_state['error'] = None
        job_state['scheduler_job_num'] = result['job_num']
        os.chdir(ret_dir)
        if job_state['_marked_for_del']:
            _delete_job(job_state)
            return (-2, 'Job %d deleted' % job_id)

    return (0, 'Job scheduled')

def job_postprocess(job_id, job_state_file=None):
    """Run bin/onramp_postprocess.py for job_id and update state to reflect.

    Args:
        job_id (int): Id of the job to launch bin/onramp_postprocess.py for.

    Returns:
        Tuple with 0th position being error code and 1st position being string
        indication of status.
    """
    _logger.info('PCE.tools.jobs._job_postprocess() called')

    # Get attrs needed.
    with JobState(job_id, job_state_file) as job_state:
        username = job_state['username']
        mod_id = job_state['mod_id']
        run_name = job_state['run_name']
        mod_name = job_state['mod_name']
        run_dir = job_state['run_dir']
    args = (username, mod_name, mod_id, run_name)
    ret_dir = os.getcwd()

    os.chdir(run_dir)
    _logger.debug('Calling bin/onramp_postprocess.py')
    try:
        result = check_output([os.path.join(pce_root, 'src/env/bin/python'),
                               'bin/onramp_postprocess.py'], stderr=STDOUT)
    except CalledProcessError as e:
        code = e.returncode
        if code > 127:
            code -= 256
        result = e.output
        msg = ('Postprocess exited with return status %d and output: %s'
               % (code, result))
        with JobState(job_id, job_state_file) as job_state:
            job_state['state'] = 'Postprocess failed'
            job_state['error'] = msg
            _logger.error(msg)
            os.chdir(ret_dir)
            if job_state['_marked_for_del']:
                _delete_job(job_state)
                return (-2, 'Job %d deleted' % job_id)
        return (-1, msg)
    finally:
        module_log(run_dir, 'postprocess', result)

    # Grab job output.
    with open('output.txt', 'r') as f:
        output = f.read()
    os.chdir(ret_dir)

    # Update state.
    with JobState(job_id, job_state_file) as job_state:
        job_state['state'] = 'Done'
        job_state['error'] = None
        job_state['output'] = output
        if job_state['_marked_for_del']:
            _delete_job(job_state)
            return (-2, 'Job %d deleted' % job_id)

def _get_module_status_output(job_id, job_state_file=None):
    """Run bin/onramp_status.py for job and return any output.

    Args:
        job_id (int): Id of the job to launch bin/onramp_status.py for.

    Returns:
        String containint output to stdout and stderr frob job's
        bin/onramp_status.py script.
    """
    # Get attrs needed.
    with JobState(job_id, job_state_file) as job_state:
        username = job_state['username']
        mod_id = job_state['mod_id']
        run_name = job_state['run_name']
        mod_name = job_state['mod_name']
        run_dir = job_state['run_dir']
    #args = (username, mod_name, mod_id, run_name)
    #run_dir = os.path.join(pce_root, 'users/%s/%s_%d/%s' % args)
    ret_dir = os.getcwd()

    # Run bin/onramp_status.py and grab output.
    os.chdir(run_dir)
    _logger.debug('Calling bin/onramp_status.py')
    try:
        output = check_output([os.path.join(pce_root, 'src/env/bin/python'),
                               'bin/onramp_status.py'], stderr=STDOUT)
    except CalledProcessError as e:
        code = e.returncode
        if code > 127:
            code -= 256
        output = ('Status exited with return status %d and output: %s'
               % (code, e.output))

    module_log(run_dir, 'status', output)
    os.chdir(ret_dir)
    return output

def _build_job(job_id, job_state_file=None):
    """Launch actions required to maintain job state and/or currate job results
    and return the state.

    When current job state (as a function of both PCE state tracking and
    scheduler output) warrants, initiate job postprocessing and/or status
    checking prior to building and returning state.

    Args:
        job_id (int): Id of the job to get state for.

    Returns:
        OnRamp formatted dictionary containing job attrs.
    """
    status_check_states = ['Scheduled', 'Queued', 'Running']
    with JobState(job_id, job_state_file) as job_state:
        _logger.debug('Building at %s' % time.time())
        if 'state' not in job_state.keys():
            _logger.debug('No state at %s' % time.time())
            _logger.debug('job_state keys: %s' % job_state.keys())
            return {}

        if job_state['state'] in status_check_states:
            specfile = os.path.join(pce_root, 'src', 'configspecs',
                                    'onramp_pce_config.cfgspec')
            cfg = ConfigObj(os.path.join(pce_root, 'bin',
                                         'onramp_pce_config.cfg'),
                            configspec=specfile)
            cfg.validate(Validator())
            scheduler = Scheduler(cfg['cluster']['batch_scheduler'])
            sched_job_num = job_state['scheduler_job_num']
            job_status = scheduler.check_status(sched_job_num)

            # Bad.
            if job_status[0] != 0:
                _logger.debug('Bad job status: %s' % job_status[1])
                job_state['state'] = 'Run failed'
                job_state['error'] = job_status[1]
                if job_status[0] != -2:
                    job_state['state'] = job_status[1]
                if job_state['_marked_for_del']:
                    _delete_job(job_state)
                    # FIXME: This might cause trouble. About to return {}.
                    return copy.deepcopy(job_state)
                return copy.deepcopy(job_state)

            # Good.
            if job_status[1] in ['Done', 'No info']:
                job_state['state'] = 'Postprocessing'
                if job_state['_marked_for_del']:
                    _delete_job(job_state)
                    # FIXME: This might cause trouble. About to return {}.
                    return copy.deepcopy(job_state)
                job_state['error'] = None
                job_state['mod_status_output'] = None
                p = Process(target=job_postprocess, args=(job_id, job_state_file))
                p.start()
            elif job_status[1] == 'Running':
                job_state['state'] = 'Running'
                job_state['error'] = None
                if job_state['_marked_for_del']:
                    _delete_job(job_state)
                    # FIXME: This might cause trouble. About to return {}.
                    return copy.deepcopy(job_state)
                mod_status_output = _get_module_status_output(job_id,
                                                              job_state_file)
                job_state['mod_status_output'] = mod_status_output
            elif job_status[1] == 'Queued':
                job_state['state'] = 'Queued'
                job_state['error'] = None
                if job_state['_marked_for_del']:
                    _delete_job(job_state)
                    # FIXME: This might cause trouble. About to return {}.
                    return copy.deepcopy(job_state)

        job = copy.deepcopy(job_state)

    if job['state'] in ['Launch failed', 'Setting up launch']:
        return job

    # Build visible files.
    _logger.debug('job state: %s' % str(job))
    dir_args = (job['username'], job['mod_name'], job['mod_id'],
                job['run_name'])
    run_dir = os.path.join(pce_root, 'users/%s/%s_%d/%s' % dir_args)
    cfg_file = os.path.join(run_dir, 'config/onramp_metadata.cfg')
    try:
        conf = ConfigObj(cfg_file, file_error=True)
    except (IOError, SyntaxError):
        # Badly formed or non-existant config/onramp_metadata.cfg.
        _logger.debug('Bad metadata')
        _logger.debug(cfg_file)
        return job

    if 'onramp' in conf.keys() and 'visible' in conf['onramp'].keys():
        globs = conf['onramp']['visible']
        if isinstance(globs, basestring):
            # Globs is only a single string. Convert to list.
            globs = [globs]
    else:
        globs = []

    ret_dir = os.getcwd()
    os.chdir(run_dir)
    filenames = [
        name for name in
        chain.from_iterable(
            map(glob.glob, globs)
        )
    ]

    prefix = os.path.join(pce_root, 'users') + '/'
    url_prefix = run_dir.split(prefix)[1]

    job['visible_files'] = [{
            'name': filename,
            'size': os.path.getsize(os.path.join(run_dir, filename)),
            'url': os.path.join('files', os.path.join(url_prefix, filename))
        } for filename in filenames
    ]
    os.chdir(ret_dir)

    return job

def _clean_job(job):
    """Remove and key/value pairs from job where the key is prefixed by an
    underscore.

    Args:
        job (JobState): The job to clean.

    Returns:
        JobState with all underscore-prefixed keys removed.
    """
    for key in job.keys():
        if key.startswith('_'):
            job.pop(key, None)
    return job

def get_jobs(job_id=None, job_state_file=None):
    """Return list of tracked jobs or single job.

    Kwargs:
        job_id (int/None): If int, return jobs resource with corresponding id.
            If None, return list of all tracked job resources.

    Returns:
        OnRamp formatted dict containing job attrs for each job requested.
    """
    if job_id:
        return _clean_job(_build_job(job_id, job_state_file))

    return [_clean_job(_build_job(job_id)) for job_id in
            filter(lambda x: not x.startswith('.'),
                   os.listdir(_job_state_dir))]

def init_job_delete(job_id):
    """Initiate the deletion of a job.

    If job is in a state where deletion is an acceptable action, job will
    be deleted immediately. If not, job will be marked for deletion.
    Transistions from unacceptable delete states to acceptable delete states
    should check the job to see if deletion has been requested.

    Args:
        job_id (int): Id of the job to delete.

    Returns:
        Tuple with 0th position being error code and 1st position being string
        indication of status.
    """
    job_cancel_states = ['Scheduled', 'Queued', 'Running']
    accepted_states = ['Launch failed', 'Schedule failed', 'Preprocess failed',
                       'Run failed', 'Postprocess failed', 'Done']
    accepted_states += job_cancel_states

    with JobState(job_id) as job_state:
        if 'state' not in job_state.keys():
            return (-1, 'Job %d does not exist' % job_id)
        state = job_state['state']
        if state in accepted_states:
            _delete_job(job_state)
            return (0, 'Job %d deleted' % job_id)

        job_state['_marked_for_del'] = True
        return (0, 'Job %d marked for deletion' % job_id)
        
def _delete_job(job_state):
    """Delete given job.

    Both state for and contents of job will be removed.

    Args:
        job_state (JobState): State object for the job to remove.
    """
    job_cancel_states = ['Scheduled', 'Queued', 'Running']
    if job_state['state'] in job_cancel_states:
        cfgfile = os.path.join(pce_root, 'bin', 'onramp_pce_config.cfg')
        specfile = os.path.join(pce_root, 'src', 'configspecs',
                                'onramp_pce_config.cfgspec')
        cfg = ConfigObj(cfgfile, configspec=specfile)
        cfg.validate(Validator())
        scheduler = Scheduler(cfg['cluster']['batch_scheduler'])
        result = scheduler.cancel_job(job_state['scheduler_job_num'])
        _logger.debug('Cancel job output: %s' % result[1])
    job_state_file = os.path.join(_job_state_dir, str(job_state['job_id']))
    os.remove(job_state_file)
    args = (job_state['username'], job_state['mod_name'], job_state['mod_id'],
            job_state['run_name'])
    run_dir = os.path.join(pce_root, 'users/%s/%s_%d/%s' % args)
    shutil.rmtree(run_dir, ignore_errors=True)
    job_state.clear()
