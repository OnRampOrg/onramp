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
import argparse
import os
import shutil
import sys
import time
from subprocess import call, check_output
from tempfile import TemporaryFile

from configobj import ConfigObj
from validate import Validator
from os.path import abspath, expanduser

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

    Usage: onramp_pce_service.py modtest [-h] [-v] mod_ini_file

    positional arguments:
        mod_ini_file   module's modtest configuration file

    optional arguments:
        -h, --help     show help message and exit
        -v, --verbose  increase output verbosity
    """
    descrip = 'Test contents of OnRamp educational module.'
    parser = argparse.ArgumentParser(prog='onramp_pce_service.py modtest',
                                     description=descrip)
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='increase output verbosity')
    parser.add_argument('mod_ini_file',
                        help="module's modtest configuration file")
    args = parser.parse_args(args=sys.argv[2:])

    os.chdir('../')
    ret_dir = os.getcwd()
    env_py = os.path.abspath('src/env/bin/python')

    conf = ConfigObj(args.mod_ini_file,
                     configspec='src/configspecs/modtest.inispec')
    conf.validate(Validator())

    deploy_path = abspath(expanduser(conf['deploy_path']))
    module_path = abspath(expanduser(conf['module_path']))

    shutil.copytree(module_path, deploy_path)

    os.chdir(deploy_path)
    post_deploy_test = abspath(expanduser(conf['post_deploy_test']))
    post_preprocess_test = abspath(expanduser(conf['post_preprocess_test']))
    post_launch_test = abspath(expanduser(conf['post_launch_test']))
    post_status_test = abspath(expanduser(conf['post_status_test']))
    post_postprocess_test = abspath(expanduser(conf['post_postprocess_test']))
    custom_runparams = abspath(expanduser(conf['custom_runparams']))
    
    # Deploy.
    os.chdir(deploy_path)
    if args.verbose:
        print 'Running bin/onramp_deploy.py'
    # FIXME: This needs to be able to handle the 'admin required' situation:
    call([env_py, 'bin/onramp_deploy.py'])
    if conf['post_deploy_test']:
        if args.verbose:
            print 'Running post_deploy_test'
        if 0 != call([env_py, post_deploy_test]):
            print 'post_deploy_test failed.'
            _modtest_cleanup(conf, deploy_path)
            return
    os.mkdir('onramp')
    if conf['custom_runparams']:
        if args.verbose:
            print 'Simulating generation of onramp_runparams.ini'
        shutil.copyfile(custom_runparams, 'onramp_runparams.ini')
    os.chdir(ret_dir)

    # Preprocess.
    os.chdir(deploy_path)
    if args.verbose:
        print 'Running bin/onramp_preprocess.py'
    call([env_py, 'bin/onramp_preprocess.py'])
    if conf['post_preprocess_test']:
        if args.verbose:
            print 'Running post_preprocess.py'
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
        if args.verbose:
            print 'Launching job'
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
        if args.verbose:
            print 'Running post_launch_test'
        if 0 != call([env_py, post_launch_test]):
            print 'post_launch_test failed.'
            _modtest_cleanup(conf, deploy_path)
            return
    os.chdir(ret_dir)
        
    # Wait for job to finish, call onramp_status.py when appropriate.
    os.chdir(deploy_path)
    if args.verbose:
        print 'Waiting/polling job state for completion'
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
            if os.path.isfile('output.txt'):
                if conf['cleanup']:
                    print ('modtest is configured to cleanup job files on '
                           'exit, but there has been an error. Would you like '
                           'to keep the files for troubleshooting?')
                    response = raw_input('(Y)es or (N)o? ')
                    if response == 'Y' or response == 'y':
                        conf['cleanup'] = False
                        print ('Output file from job: %s'
                               % deploy_path + '/output.txt')
                else:
                    print ('Output file from job: %s'
                           % deploy_path + '/output.txt')
            else:
                print 'No output file from job found.'

            _modtest_cleanup(conf, deploy_path)
            return

        if job_state == 'Running':
            if args.verbose:
                print 'Running bin/onramp_status.py'
            print 'bin/onramp_status.py output:'
            try:
                print check_output([env_py, 'bin/onramp_status.py'])
            except CalledProcessError:
                print 'bin/onramp_status.py call failed.'
                _modtest_cleanup(conf, deploy_path)
                return
            if conf['post_status_test']:
                if args.verbose:
                    print 'Running post_status_test'
                if 0 != call([env_py, post_status_test]):
                    print 'post_status_test failed.'
                    _modtest_cleanup(conf, deploy_path)
                    return

    # Postprocess.
    if args.verbose:
        print 'Running bin/onramp_postprocess.py'
    call([env_py, 'bin/onramp_postprocess.py'])
    if conf['post_postprocess_test']:
        if args.verbose:
            print 'Running post_process_test'
        if 0 != call([env_py, post_postprocess_test]):
            print 'post_postprocess_test failed.'
            _modtest_cleanup(conf, deploy_path)
            return
    os.chdir(ret_dir)

    # Print results if small enough.
    os.chdir(deploy_path)
    if os.path.isfile('output.txt'):
        output_stat = os.stat('output.txt')
        if output_stat.st_size > 320:
            if conf['cleanup']:
                print ('modtest is configured to cleanup job files on '
                       'exit, but output.txt is to large to print. Would you like '
                       'to keep the files to view output.txt?')
                response = raw_input('(Y)es or (N)o? ')
                if response != 'Y' and response != 'y':
                    _modtest_cleanup(conf, deploy_path)
                    return
            print ('Results file: %s' % deploy_path + '/output.txt')
        else:
            print 'Results:'
            with open('output.txt', 'r') as f:
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
        if sys.argv[1] not in switch.keys():
            raise ValueError()
    except (IndexError, KeyError, ValueError):
        print __doc__
        sys.exit(-1)

    switch[sys.argv[1]]()
