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
    pce_dir = 'onramp'
    batch_script_name = 'script.sh'
    default_sleep_time = 5.0
    job_output_file = 'output.txt'
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
    custom_runparams = abspath(expanduser(conf['custom_runparams']))
    post_deploy_test = ('post_deploy_test',
                        abspath(expanduser(conf['post_deploy_test'])))
    post_preprocess_test = ('post_preprocess_test',
                        abspath(expanduser(conf['post_preprocess_test'])))
    post_launch_test = ('post_launch_test',
                        abspath(expanduser(conf['post_launch_test'])))
    post_status_test = ('post_status_test',
                        abspath(expanduser(conf['post_status_test'])))
    post_postprocess_test = ('post_postprocess_test',
                        abspath(expanduser(conf['post_postprocess_test'])))

    def finish(conf, error=False):
        path = deploy_path
        results = job_output_file
        params = args

        if os.path.isfile(results):
            if error:
                if conf['cleanup']:
                    print ('modtest is configured to cleanup job files on '
                           'exit, but there has been an error. Would you like '
                           'to keep the files for troubleshooting?')
                    response = raw_input('(Y)es or (N)o? ')
                    if response == 'Y' or response == 'y':
                        conf['cleanup'] = False
                        print ('Output file from job: %s'
                               % os.path.join(deploy_path, results))
                else:
                    print ('Output file from job: %s'
                           % os.path.join(deploy_path, results))
            else:
                if not conf['cleanup']:
                    print ('Output file from job: %s'
                           % os.path.join(deploy_path, results))
        else:
            print 'No output file found.'

        if conf['cleanup']:
            if params.verbose:
                print 'Removing %s' % deploy_path
            shutil.rmtree(path)

    def run_section(script=None, test=None, print_output=False):
        py = env_py
        params = args
        cfg = conf

        if script:
            if params.verbose:
                print 'Running %s' % script
            try:
                # FIXME: This needs to be able to handle the 'admin required'
                # situation when script = 'bin/onramp_deploy'
                output = check_output([py, script])
            except CalledProcessError:
                print '%s call failed.' % script
                finish(conf, error=True)
                return

        if print_output:
            print output

        if test:
            if cfg[test[0]]:
                if params.verbose:
                    print 'Running %s' % test[0]
                if 0 != call([py, test[1]]):
                    print '%s failed.' % test[0]
                    finish(cfg, error=True)
                    return

    def SLURM_status(job_num):
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

    # Deploy.
    run_section(script='bin/onramp_deploy.py', test=post_deploy_test)
    os.mkdir(pce_dir)
    if conf['custom_runparams']:
        if args.verbose:
            print 'Simulating generation of onramp_runparams.ini'
        shutil.copyfile(custom_runparams, 'onramp_runparams.ini')

    # Preprocess.
    run_section(script='bin/onramp_preprocess.py', test=post_preprocess_test)
        
    # Run.
    if conf['batch_scheduler'] == 'SLURM':
        status_check = SLURM_status
        tools._build_SLURM_script('modtest', conf['num_tasks'], None,
                                filename=batch_script_name)
        if args.verbose:
            print 'Launching job'
        try:
            batch_output = check_output(['sbatch', batch_script_name])
            job_num = batch_output.strip().split()[3:][0] 
        except (CalledProcessError, ValueError, IndexError):
            print 'Job scheduling call failed or gave unexpected output.'
            finish(conf, error=True)
            return
    else:
        print "Invalid value given for 'batch_scheduler'."
        finish(conf, error=True)
        return

    run_section(test=post_launch_test)
        
    # Wait for job to finish, call onramp_status.py when appropriate.
    if args.verbose:
        print 'Waiting/polling job state for completion'
        
    sleep_time = conf['results_check_sleep']
    job_state = 'Queued'

    while job_state != 'Done':
        time.sleep(sleep_time)
        (status, job_state) = status_check(job_num)

        if 0 != status:
            print 'Job info call failed.'
            finish(conf, error=True)
            return

        if job_state == 'Running':
            run_section(script='bin/onramp_status.py', test=post_status_test,
                        print_output=True)

    # Postprocess.
    run_section(script='bin/onramp_postprocess.py', test=post_postprocess_test)

    if args.verbose:
        print 'No errors found.'

    finish(conf)

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
