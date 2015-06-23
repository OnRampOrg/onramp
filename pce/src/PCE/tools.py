"""Support functionality needed to communicate with onramp REST clients,
administer system users, and launch parallel jobs.

Exports:
    launch_job: Launch a parallel job on system.
    encrypt: Encrypt a message.
    decrypt: Decript a message.
    create_admin: Create admin user with default settings.
    authenticate: Authenticate a user.
    admin_authenticate: Authenticate an admin user.
"""

import glob
import hashlib
import json
import logging
import os

from Crypto import Random
from Crypto.Cipher import AES

from subprocess import call, check_output

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
        retval = 'Project Location does not exist.'
        logger.error(retval)
        return retval

    ret_dir = os.getcwd()

    # Begin Executing the Job
    os.chdir(project_loc)
    logger.info('Calling bin/onramp_preprocess.py in %s' % project_loc)
    call(['python', 'bin/onramp_preprocess.py'])

    logger.debug('Server configured to use %s as batch scheduler'
                 % batch_scheduler)

    if batch_scheduler == 'SLURM':
        _build_SLURM_script(run_name, numtasks, email,
                            filename=project_loc + '/script.sh')
        call(['sbatch', 'script.sh'])
    elif batch_scheduler == 'SGE':
        _build_SGE_script(run_name, numtasks, email,
                          filename=project_loc + 'script.sh')
        call(['qsub', 'script.sh'])
    else:
        retval = 'Invalid argument for batch_scheulder'
        logger.error(retval)
        return retval

    os.chdir(ret_dir)
    logger.info('Job %s scheduled' % run_name)
    return 'Complete!'

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
    contents += '#SBATCH -o Results/output.txt\n'
    contents += '#SBATCH -n ' + str(numtasks) + '\n'
    if email:
        logger.debug('%s configured for email reporting to %s'
                     % (run_name, email))
        contents += '#SBATCH --mail-user=' + email + '\n'
    contents += '###################################\n'
    contents += '\n'
    contents += 'python bin/onramp_run.py\n'

    script_file = open(filename, 'w')
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
    contents += '#$ -o Results/output.txt\n'
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
