"""Support functionality needed to communicate with OnRamp REST clients,
administer system users, and launch parallel jobs.

Exports:
    get_visible_file: Verify access allowed to requested file and return it.
    module_log: Log a message to one of the log/onramp_*.log files in a module.
    launch_job: Launch a parallel job on system. DEPRECATED.
    encrypt: Encrypt a message. DEPRECATED.
    decrypt: Decript a message. DEPRECATED.
    create_admin: Create admin user with default settings. DEPRECATED.
    authenticate: Authenticate a user. DEPRECATED.
    admin_authenticate: Authenticate an admin user. DEPRECATED.
    modules: Functionality for working with OnRamp educational modules. DEPRECATED.
"""

import glob
import hashlib
import json
import logging
import os
from datetime import datetime
from subprocess import CalledProcessError, call, check_output

from configobj import ConfigObj
from Crypto import Random
from Crypto.Cipher import AES

from PCEHelper import pce_root

def get_visible_file(dirs):
    """Verify access allowed to requested file and return it.

    Args:
        dirs (list of str): Ordered list of folder names between base_dir
            (currently onramp/pce/users) and specific file.
    """
    num_parent_dirs = 3
    if len(dirs) <= num_parent_dirs or '..' in dirs:
        return (-4, 'Bad request')

    run_dir = os.path.join(os.path.join(pce_root, 'users'),
                           '/'.join(dirs[:num_parent_dirs]))
    filename = os.path.join(run_dir, '/'.join(dirs[num_parent_dirs:]))

    ini_file = os.path.join(run_dir, 'config/onramp_metadata.ini')
    try:
        conf = ConfigObj(ini_file, file_error=True)
    except (IOError, SyntaxError):
        return (-3, 'Badly formed or non-existant config/onramp_metadata.ini') 

    if 'onramp' in conf.keys() and 'visible' in conf['onramp'].keys():
        globs = conf['onramp']['visible']
        if isinstance(globs, basestring):
            # Globs is only a single string. Convert to list.
            globs = [globs]
    else:
        globs = []


    if not os.path.isfile(filename):
        return (-2, 'Requested file not found') 

    for entry in globs:
        if filename in glob.glob(os.path.join(run_dir, entry)):
            return (0, open(os.path.join(run_dir, filename), 'r'))

    return (-1, 'Requested file not configured to be visible')

def module_log(mod_root, log_id, msg):
    """Log a message to one of the log/onramp_*.log files in a module.

    Overwrite existing log entry if any. Prefix message with preamble,
    timestamp, and blank line.

    Args:
        mod_root (str): Absolute path of module root folder.
        log_id (str): Determines logfile to use: log/onramp_{log_id}.log.
        msg (str): Message to be logged.
    """
    logname = os.path.join(mod_root, 'log/onramp_%s.log' % log_id)
    with open(logname, 'w') as f:
        f.write('The following output was logged %s:\n\n' % str(datetime.now()))
        f.write(msg)
        
    
# Everything below is deprecated. ----------------------------------------------

def launch_job(project_loc, run_name, batch_scheduler, numtasks=4, email=None,
               **kwargs):
    """Launch a parallel job on the system.

    Args:
        project_loc (str): Filesystem path for the root folder of the project.
        run_name (str): Name for this particular run of the project.
        batch_scheduler (str): Identifier of chosen batch_scheduler.

    Kwargs:
        numtasks: Number of tasks the job should use. Default: 4
        email (str): If not 'None', email results to this address. Default: None

    Returns:
        str: Status message indicating state of job launch, or errors
            encountered.
    """
    logger = logging.getLogger('onramp')
    logger.debug('PCE.tools.launch_job() called')

    # Verify if project_loc exists, if not return with message.
    if not os.path.isdir(project_loc):
        msg = 'Project Location does not exist.'
        logger.error(msg)
        return {
            'status_code': -6,
            'status_msg': msg
        }

    ret_dir = os.getcwd()

    # Begin Executing the Job
    os.chdir(project_loc)
    logger.info('Calling bin/onramp_preprocess.py in %s' % project_loc)
    call(['../../../../src/env/bin/python', 'bin/onramp_preprocess.py'])

    logger.debug('Server configured to use %s as batch scheduler'
                 % batch_scheduler)

    if batch_scheduler == 'SLURM':
        _build_SLURM_script(run_name, numtasks, email,
                            filename=project_loc + '/script.sh')

        try:
            batch_output = check_output(['sbatch', 'script.sh'])
        except CalledProcessError as e:
            msg = 'Job scheduling call failed'
            logger.error(msg)
            os.chdir(ret_dir)
            return {
                'status_code': -4,
                'status_msg': msg,
                'return_code': e.returncode,
                'output': e.output
            }

        output_fields = batch_output.strip().split()

        if 'Submitted batch job' != ' '.join(output_fields[:-1]):
            msg = 'Unexpeted output from sbatch'
            self.logger.error(msg)
            return {
                'status_code': -7,
                'status_msg': msg
            }

        try:
            job_num = int(output_fields[3:][0])
        except ValueError, IndexError:
            msg = 'Unexpeted output from sbatch'
            self.logger.error(msg)
            return {
                'status_code': -7,
                'status_msg': msg
            }

    elif batch_scheduler == 'SGE':
        _build_SGE_script(run_name, numtasks, email,
                          filename=project_loc + 'script.sh')
        try:
            batch_output = check_output(['qsub', 'script.sh'])
        except CalledProcessError as e:
            msg = 'Job scheduling call failed'
            logger.error(msg)
            os.chdir(ret_dir)
            return {
                'status_code': -4,
                'status_msg': msg,
                'return_code': e.returncode,
                'output': e.output
            }

    else:
        msg = 'Invalid argument for batch_scheulder'
        logger.warn(msg)
        os.chdir(ret_dir)
        return {
            'status_code': -5,
            'status_msg': msg
        }

    os.chdir(ret_dir)
    msg = 'Job %s scheduled as job_num: %s' % (run_name, job_num)
    logger.info(msg)
    return {'status_code': 0, 'status_msg': msg, 'job_num': job_num}

def _build_SLURM_script(run_name, numtasks, email, filename='script.sh'):
    """Build a SLURM formatted batch script for the job.

    Build prologue and epilogue sections of the batch script which surround the
    run section of the script. The run section of the script consists solely of
    a call to 'python bin/onramp_run.py' from the path specified by
    run_name.

    Args:
        run_name (str): Name for the particular run of the job.
        numtasks: Number of tasks the job should use. Default: 4
        email (str): If not 'None', email results to this address. Default: None
    
    Keyword Args:
        filename (str): Name of the generated file. Default: 'script.sh'.
    """
    logger = logging.getLogger('onramp')
    logger.debug('PCE.tools._build_SLURM_script() called')

    contents = '#!/bin/bash\n'
    contents += '\n'
    contents += '###################################\n'
    contents += '# Slurm Submission options\n'
    contents += '#\n'
    contents += '#SBATCH --job-name=' + run_name + '\n'
    contents += '#SBATCH -o output.txt\n'
    contents += '#SBATCH -n ' + str(numtasks) + '\n'
    if email:
        logger.debug('%s configured for email reporting to %s'
                     % (run_name, email))
        contents += '#SBATCH --mail-user=' + email + '\n'
    contents += '###################################\n'
    contents += '\n'
    contents += 'python bin/onramp_run.py\n'

    script_file = open(filename, 'w')
    logger.debug('Writing batch script to %s' % filename)
    script_file.write(contents)
    script_file.close()
    logger.info('SLURM script written for %s' % run_name)

def _build_SGE_script(run_name, numtasks, email, filename='script.sh'):
    """Build a SGE formatted batch script for the job.

    Build prologue and epilogue sections of the batch script which surround the
    run section of the script. The run section of the script consists solely of
    a call to 'python bin/onramp_run.py' from the path specified by
    run_name.

    Args:
        run_name (str): Name for the particular run of the job.
        numtasks: Number of tasks the job should use. Default: 4
        email (str): If not 'None', email results to this address. Default: None
    
    Keyword Args:
        filename (str): Name of the generated file. Default: 'script.sh'.
    """
    logger = logging.getLogger('onramp')
    logger.debug('PCE.tools._build_SGE_script() called')

    contents = '#!/bin/bash\n'
    contents += '###################################\n'
    contents += '# SGE Submission options\n'
    contents += '#\n'
    contents += '# Name of the job\n'
    contents += '#$ -N ' + run_name + '\n'
    contents += '#\n'
    contents += '# Changes the working directory to where the job has been \n'
    contents += '# submitted, otherwise uses the home directory\n'
    contents += '#$ -cwd\n'
    contents += '#\n'
    contents += '# Merge the normal output and error messages into one file\n'
    contents += '#$ -j y\n'
    contents += '#\n'
    contents += '# Pass all environment variables to the job\n'
    contents += '#$ -V\n'
    contents += '#\n'
    contents += '# Restarts the job if the system crashes or is rebooted. This \n'
    contents += '# does not apply if the job itself crashes\n'
    contents += '#$ -r y\n'
    contents += '#\n'
    contents += '# Define the output file\n'
    contents += '#$ -o output.txt\n'
    contents += '#\n'
    ## qsub will wait for the job to complete before exiting:
    # contents += '#$ -sync y\n'
    ## increment based on number of requested processors:
    # contents += '#$ -pe orte 4\n'
    ## Request time for this job (max time) - 5 minutes:
    # contents += '#$ l h_rt=00:05:00\n'
    contents += '# Define the command interpreter to be used\n'
    contents += '#$ -S /bin/bash\n'
    contents += '###################################\n'
    contents += '\n'
    contents += 'python bin/onramp_run.py\n'
    contents += '\n'
    if email:
        logger.debug('%s configured for email reporting to %s'
                     % (run_name, email))
        contents += '#$ -m be\n'
        contents += '#$ -M ' + email + '\n'

    script_file = open(filename, 'w')
    script_file.write(contents)
    script_file.close()
    logger.info('SGE script written for %s' % run_name)


def encrypt(message, key):
    """Encrypt a message.

    Args:
        message (str): Message to be encrypted.
        key (str): Encryption key.

    Returns:
        str: Encrypted message as ciphertext.
    """
    logger = logging.getLogger('onramp')
    logger.debug('PCE.tools.encrypt() called')
    def pad(s):
        x = AES.block_size - len(s) % AES.block_size
        return s + (chr(x) * x)

    padded_message = pad(message)

    iv = Random.OSRNG.posix.new().read(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)

    return iv + cipher.encrypt(padded_message)

def decrypt(ciphertext, key):
    """Decrypt a message.

    Args:
        message (str): Message to be decrypted.
        key (str): Decryption key.

    Returns:
        str: Plaintext message decrypted from ciphertext.
    """
    logger = logging.getLogger('onramp')
    logger.debug('PCE.tools.decrypt() called')
    unpad = lambda s: s[:-ord(s[-1])]
    iv = ciphertext[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext))[AES.block_size:]

    return plaintext

def create_admin(base_dir):
    """Create a default admin user.

    Created user wil have username: 'admin' and password: 'admin'. Credentials
    for the user will be stored in base_dir/admin/security.

    Args:
        base_dir (str): Filesystem path of the users dir.
    """
    logger = logging.getLogger('onramp')
    logger.debug('PCE.tools.create_admin() called')
    username = 'admin'
    password = 'admin'
    user_dir = base_dir + '/' + username

    logger.info('Creating dir for new admin user at %s' % user_dir)
    call(['mkdir', user_dir])

    content = json.dumps([username, 'true'], ensure_ascii=False)
    key = hashlib.sha256(password).digest()
    encrypted = encrypt(content, key)
    decrypted = decrypt(encrypted, key)

    securityfile = open(user_dir + '/security', 'w')
    securityfile.write(encrypted)
    securityfile.close()

def authenticate(dir_path, user, password):
    """Authenticate the given user.

    Args:
        dir_path (str): Filesystem path to dir for user.
        user (str): Username.
        password (str): User's password.

    Returns:
        str: None on successful authentication of user. Indication of error on
            failure.
    """
    logger = logging.getLogger('onramp')
    logger.debug('PCE.tools.authenticate() called')
    if not os.path.isdir(dir_path):
        retval = 'Specified user does not exist.'
        logger.warning(retval)
        return retval
    
    if not os.path.isfile(dir_path + '/security'):
        logger.error('Security file does not exist for %s' % user)
        return ('Security file does not exist for ' + user
                + '. Please contact your parallel computer administrator to '
                + 'recreate this file.')
    
    secure_user = ''
    securityfile = open(dir_path + '/security')
    while True:
        read_data = securityfile.read(8192)
        if not read_data:
            break
        secure_user += read_data
    
    key = hashlib.sha256(password).digest()
    decrypted_content = ''
    try:
        decrypted_content = json.loads(decrypt(secure_user, key))
    except:
        retval = 'Incorrect password.'
        logger.warning(retval)
        return retval
    
    username = decrypted_content[0]
    is_admin = decrypted_content[1]
    
    if username != user:
        retval = 'Incorrect password.'
        logger.warning(retval)
        return retval

    logger.info('User %s has been authenticated' % user)
    return None

def admin_authenticate(dir_path, user, password):
    """Authenticate the given admin user.

    Args:
        dir_path (str): Filesystem path to dir for user.
        user (str): Username.
        password (str): User's password.

    Returns:
        str: None on successful admin authentication of user. Indication of
            error on failure.
    """
    logger = logging.getLogger('onramp')
    logger.debug('PCE.tools.admin_authenticate() called')
    if not os.path.isdir(dir_path):
        retval = 'Specified admin does not exist.'
        logger.warning(retval)
        return retval
    
    if not os.path.isfile(dir_path + '/security'):
        logger.error('Security file does not exist for ' % user)
        return ('Security file does not exist for ' + user
                + '. Please contact your parallel computer administrator to '
                + 'recreate this file.')
    
    secure_user = ''
    securityfile = open(dir_path + '/security')
    while True:
        read_data = securityfile.read(8192)
        if not read_data:
            break
        secure_user += read_data
    
    key = hashlib.sha256(password).digest()
    decrypted_content = ''
    try:
        decrypted_content = json.loads(decrypt(secure_user, key))
    except:
        retval = 'Incorrect password.'
        logger.warning(retval)
        return retval
    
    username = decrypted_content[0]
    is_admin = decrypted_content[1]
    
    if username != user:
        retval = 'Incorrect password.'
        logger.warning(retval)
        return retval

    if is_admin != 'true':
        retval = 'User %s is not an admin.' % user
        logger.warning(retval)
        return retval

    logger.info('Admin user %s has been authenticated' % user)
    return None

if __name__ == '__main__':
    launch_job('../../modules/HelloMPI', 'hello-mpi', 4, 'false', 'false',
               'false', 'test', None)
