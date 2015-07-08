#!src/env/bin/python
"""Control the onramp REST server.

Usage: ./onramp_service.py COMMAND [COMMAND_ARGS]

Commands:
    start
        Starts the OnRamp PCE Server.

    stop
        Stops the OnRamp PCE Server.

    restart
        Restarts the OnRamp PCE Server.

    modtest TEST_CONFIG_FILE
        Tests the contents of an OnRamp Educational module as specified by
        params in TEST_CONFIG_FILE.
"""
import os
import shutil
import sys
import time
from subprocess import call, check_output
from tempfile import TemporaryFile

from configobj import ConfigObj
from validate import Validator

from PCE import tools

_pidfile = '.onrampRESTservice.pid'
_src_dir = 'src'
_script_name = 'RESTservice.py'

def _getPID():
    """Get PID from specified PIDFile.
    
    Returns:
        int: >0 -- RESTservice PID
             -1 -- _pidfile contains invalid PID
             -2 -- _pidfile not found
    """
    pid = 0

    try:
        f = open(_pidfile, 'r')
        pid = int(f.read())
        f.close()
    except IOError as e:
        if e.errno == 2:
            return -2
        raise e
    except ValueError:
        return -1

    # Double check PID from PIDFile:
    outfile = TemporaryFile(mode='w+')
    call(['ps', 'x'], stdout=outfile)
    outfile.seek(0)
    for line in outfile:
        line = line.strip()
        if line.startswith(str(pid)) and line.endswith(_script_name):
            return pid

    return -1

def _start():
    """If not already running, start the REST server."""
    print 'Starting REST server...'
    pid = _getPID()

    if -2 == pid:
        # PIDFile not found, thus, server is not running.
        call(['env/bin/python', 'RESTservice.py'])
        return
    elif -1 == pid:
        print "PIDFile '%s' has been corrupted." % _src_dir + '/' +_pidfile
        return

    print 'Server appears to be already running.'
    return

def _restart():
    """If not stopped, restart the REST server, else start it."""
    print 'Restarting REST server...'
    pid = _getPID()

    if -2 == pid:
        # PIDFile not found, thus, server is not running.
        print 'REST server does not currently appear to be running.'
        _start()
        return
    elif -1 == pid:
        print "PIDFile '%s' has been corrupted." % _src_dir + '/' +_pidfile
        return

    call(['kill', '-1', str(pid)])
    return

def _stop():
    """If running, stop the REST server."""
    print 'Stopping REST server...'
    pid = _getPID()

    if -2 == pid:
        # PIDFile not found, thus, server is not running.
        print 'REST server does not currently appear to be running.'
        return
    elif -1 == pid:
        print "PIDFile '%s' has been corrupted." % _src_dir + '/' +_pidfile
        return

    call(['kill', str(pid)])

def _mod_test():
    """Test contents of OnRamp Educational module.

    Note: Requires sys.argv[2] to be filename of module test config file.
    """
    os.chdir('../')
    ret_dir = os.getcwd()
    env_py = os.path.abspath('src/env/bin/python')
    conf = ConfigObj(sys.argv[2], configspec='src/configspecs/modtest.inispec')
    conf.validate(Validator())
    deploy_path = os.path.abspath(os.path.expanduser(conf['deploy_path']))
    module_path = os.path.abspath(os.path.expanduser(conf['module_path']))
    post_deploy_test = os.path.abspath(conf['post_deploy_test'])
    post_preprocess_test = os.path.abspath(conf['post_preprocess_test'])
    post_launch_test = os.path.abspath(conf['post_launch_test'])
    post_status_test = os.path.abspath(conf['post_status_test'])
    post_postprocess_test = os.path.abspath(conf['post_postprocess_test'])
    shutil.copytree(module_path, deploy_path)
    
    # Deploy.
    os.chdir(deploy_path)
    # FIXME: This needs to be able to handle the 'admin required' situation:
    call([env_py, 'bin/onramp_deploy.py'])
    if conf['post_deploy_test']:
        if 0 != call([env_py, post_deploy_test]):
            print 'post_deploy_test failed.'
            _modtest_cleanup(conf, deploy_path)
            return
    os.mkdir('onramp')
    os.chdir(ret_dir)

    # Preprocess.
    os.chdir(deploy_path)
    call([env_py, 'bin/onramp_preprocess.py'])
    if conf['post_preprocess_test']:
        if 0 != call([env_py, post_preprocess_test]):
            print 'post_preprocess_test failed.'
            _modtest_cleanup(conf, deploy_path)
            return
    os.chdir(ret_dir)
        
    # Run.
    os.chdir(deploy_path)

    if conf['batch_scheduler'] == 'SLURM':
        status_check = _SLURM_status
        tools._build_SLURM_script('modtest', conf['num_tasks'], None,
                                filename='script.sh')
        try:
            batch_output = check_output(['sbatch', 'script.sh'])
            job_num = batch_output.strip().split()[3:][0] 
        except (CalledProcessError, ValueError, IndexError):
            print 'Job scheduling call failed or gave unexpected output.'
            _modtest_cleanup(conf, deploy_path)
            return
    else:
        print "Invalid value given for 'batch_scheduler'."
        _modtest_cleanup(conf, deploy_path)
        return

    if conf['post_launch_test']:
        if 0 != call([env_py, post_launch_test]):
            print 'post_launch_test failed.'
            _modtest_cleanup(conf, deploy_path)
            return
    os.chdir(ret_dir)
        
    # Wait for job to finish, call onramp_status.py when appropriate.
    os.chdir(deploy_path)
    if conf['results_check_sleep']:
        sleep_time = conf['results_check_sleep']
    else:
        sleep_time = 5.0
    job_state = 'Queued'
    while job_state != 'Done':
        time.sleep(sleep_time)
        (status, job_state) = status_check(job_num)
        if 0 != status:
            print 'Job info call failed.'
            _modtest_cleanup(conf, deploy_path)
            return
        if job_state == 'Running':
            print 'bin/onramp_status.py output:'
            try:
                print check_output([env_py, 'bin/onramp_status.py'])
            except CalledProcessError:
                print 'bin/onramp_status.py call failed.'
                _modtest_cleanup(conf, deploy_path)
                return
            if conf['post_status_test']:
                if 0 != call([env_py, post_status_test]):
                    print 'post_status_test failed.'
                    _modtest_cleanup(conf, deploy_path)
                    return

    # Postprocess.
    call([env_py, 'bin/onramp_postprocess.py'])
    if conf['post_postprocess_test']:
        if 0 != call([env_py, post_postprocess_test]):
            print 'post_postprocess_test failed.'
            _modtest_cleanup(conf, deploy_path)
            return
    os.chdir(ret_dir)

    # Print results.
    os.chdir(deploy_path)
    print 'Results:'
    with open('onramp/output.txt', 'r') as f:
        print f.read()

    _modtest_cleanup(conf, deploy_path)

def _modtest_cleanup(conf, deploy_path):
    """Remove deployed module if configured in conf passed to modtest.
    
    Args:
        conf (ConfigObj): Modtest configuration.
        deploy_path (str): Path to remove if configured in conf.
    """
    if conf['cleanup']:
        shutil.rmtree(deploy_path)

def _SLURM_status(job_num):
    """Get status of job launched by SLURM

    Args:
        job_num (int): Job number of job to check status of.
    """
    try:
        job_info = check_output(['scontrol', 'show', 'job', job_num])
    except CalledProcessError as e:
        print 'CalledProcessError'
        return (-1, '')

    job_state = job_info.split('JobState=')[1].split()[0]
    if job_state == 'RUNNING':
        job_state = 'Running'
    elif job_state == 'COMPLETED':
        job_state = 'Done'
    elif job_state == 'PENDING':
        job_state = 'Queued'
    else:
        print 'Unexpected job state: %s' % job_state
        return (-1, '')
    
    return (0, job_state)

switch = {
    'start': _start,
    'restart': _restart,
    'stop': _stop,
    'modtest': _mod_test
}

if __name__ == '__main__':
    os.chdir(_src_dir)
    try:
        switch[sys.argv[1]]()
    except (IndexError, KeyError):
        print __doc__
