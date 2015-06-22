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

def launch_job(project_loc, project_name, np, verbose, email, datestamps,
               email_name, batch_scheduler):
    """Launch a parallel job on the system.

    Args:
        project_loc (str): Filesystem path for the root folder of the project.
        project_name (str): Name for this particular run of the project.
        np: Number of processors to run the given project on.
        verbose (str): Pseudo-boolean val indicating whether or not output from
            the run should be generated in verbose mode. 'true', 'on', '1',
            't', 'y', and 'yes' all indicate verbose mode. All other values
            indicate not verbose.
        email (str): Pseudo-boolean val indicating whether or not output from
            the run should be emailed. 'true', 'on', '1', 't', 'y', and 'yes'
            will all set the project to be emailed. All other values will not.
            email_name is required with email is set.
        datestamps (str): Pseudo-boolean val indicating whether or not output
            from the run should be datestamped. 'true', 'on', '1', 't', 'y', and
            'yes' all set the project output to be datestamped. All other values
            do not.
        email_name (str): Email address to send output to, if configured.

    Returns:
        str: Status message indicating state of job launch, or errors
            encountered.
    """
    logger = logging.getLogger('onramp')
    logger.debug('PCE.tools.launch_job() called')

    def numprocessors(i):
        try:
            return int(i)
        except ValueError as e:
            return 4

    def eval_checkbox(s):
        return s.lower() in ['true', 'on', '1', 't', 'y', 'yes']

    # FIXME: project_name can *never* contain whitespaces because of
    # Makefile.

    np = numprocessors(np)
    verbose = eval_checkbox(verbose)
    email = eval_checkbox(email)
    datestamps = eval_checkbox(datestamps)

    # Verify if project_loc exists, if not return with message.
    if not os.path.isdir(project_loc):
        retval = 'Project Location does not exist.'
        logger.error(retval)
        return retval

    #_build_makefile(project_loc)

    # Begin Executing the Job
    os.chdir(project_loc)
    #call(['printenv'])
    logger.info('Calling make in %s' % project_loc)
    call(['make', 'c-mpi'])

    logger.debug('Server configured to use %s as batch scheduler'
                 % batch_scheduler)
    if batch_scheduler == 'SLURM':
        _build_SLURM_script(project_name, np,
                           filename=project_loc + '/script.sh')
        call(['sbatch', 'script.sh'])
    elif batch_scheduler == 'SGE':
        _build_SGE_script(project_name, np,
                          filename=project_loc + 'script.sh')
        #FIXME: If the output file already exists SGE will simply concatenate
        # more results into it, therefore we need to create a way to avoid such
        # an occurance.
        call(['qsub', 'script.sh'])
    else:
        retval = 'Invalid argument for batch_scheulder'
        logger.error(retval)
        return retval

    #FIXME: If the output file is greater than a specific size then we need
    # to notify the user that their job is complete rather than send them a
    # massive email/file.

    logger.info('Job %s scheduled' % project_name)
    return 'Complete!'

def _build_makefile(project_loc):
    """Generate default makefile at project location.

    Scan project_loc for C source and header files and use them to construct a
    makefile formatted as expected by launch_job(). Assumes the existence of a
    base makefile at ../../../Makefile relative to project_loc.
    
    ***FIXME: Method is currently hardcoded to name the main program
        'hello-mpi'. This should be changed, but currently, a strong possibility
        exists that this method will be no longer needed.

    Args:
        project_loc (str): Filesystem path for the root folder of the project.
    """
    logger = logging.getLogger('onramp')
    logger.debug('PCE.tools._build_makefile() called')
    ret_dir = os.getcwd()
    os.chdir(project_loc)
    header_files = glob.glob('*.h')

    # Check if this is a c or cpp project and either load c files or cpp
    # files. Maybe we can load both c and cpp files?
    src_files = glob.glob('*.c')

    if (len(src_files) <= 0):
        # Return an error status to the web application
        logger.error('No source files found at %s' % project_loc)
        return 'Failed to find any source files!'

    # Create the project's Makefile
    src_str = ' '.join(src_files)
    header_str = ' '.join(header_files)

    file = open('Makefile', 'w+b')
    if makefile != '':
        # Use the Makefile provided by the user.
        write(makefile)
    else:
        # Use the default Makefile.
        write('# $\Id$')
        write('PROGRAM = hello-mpi') #+ project_name)

        # FIXME: Double check source and header files. They may include
        # spaces within the filename.
        write('CSRCS = ' + src_str)
        write('INCS = ' + header_str)
        write('CLEAN = $(PROGRAM).c-mpi')
        write('all: c-mpi')
        write('c-mpi: $(CSRCS) $(INCS) $(PROGRAM).c-mpi')
        write('$(PROGRAM).c-mpi: $(CSRCS) $(INCS)')
        write('include ../../../Makefile')

    file.close()
    os.chdir(ret_dir)
    logger.info('%s written' % project_loc + '/Makefile')

def _build_SLURM_script(project_name, numtasks, filename='script.sh',
                       email=None, datestamps=False, verbose=False):
    """Build a SLURM formatted batch script for the job.

    Build prologue and epilogue sections of the batch script which surround the
    run section of the script. The run script is generated by output to STDOUT
    of setup.py found in the root directory of the project to be run. All three
    sections are put together and written to single file per args.

    Args:
        project_name (str): Name for the particular run of the job.
        numtasks: Number of tasks to run
    
    Keyword Args:
        filename (str): Name of the generated file. Default: 'script.sh'.
        email (str): Email address to send job output to. If None, batch script
            will not be configured to send email. Default: None.
        datestamps (bool): If True, datestamp the output. Default: False.
        verbose (bool): If True, output wil be verbose. Default: False.
    """
    logger = logging.getLogger('onramp')
    logger.debug('PCE.tools._build_SLURM_script() called')
    contents = '#!/bin/bash\n'
    contents += '\n'
    contents += '###################################\n'
    contents += '# Slurm Submission options\n'
    contents += '#\n'
    contents += '#SBATCH --job-name=' + project_name + '\n'
    contents += '#SBATCH -o Results/output.txt\n'
    contents += '#SBATCH -n ' + str(numtasks) + '\n'
    if email:
        logger.debug('%s configured for email reporting to %s'
                     % (project_name, email))
        contents += '#SBATCH --mail-user=' + email + '\n'
    contents += '###################################\n'
    contents += '\n'

    if datestamps:
        logger.debug('%s configured for datestamps' % project_name)
        contents += 'date\n'

    # FIXME: This needs to be communicated to CWD/setup.py:
    #if verbose:
    #    v = ' -v'
    #else:
    #    v = ''

    run_section = check_output(['../../../src/env/bin/python', 'setup.py'])
    logger.debug('Run section given by project:\n%s' % run_section)
    contents += run_section

    if datestamps:
        contents += 'date\n'

    contents += '\n'
    if email:
        contents += '#$ -m be\n'
        contents += '#$ -M ' + email+ '\n'

    script_file = open(filename, 'w')
    script_file.write(contents)
    script_file.close()
    logger.info('SLURM script written for %s' % project_name)

def _build_SGE_script(project_name, np, filename='script.sh', email=None,
                     datestamps=None, verbose=False):
    """Build a Sun Grid Engine formatted batch script for the job.

    Build prologue and epilogue sections of the batch script which surround the
    run section of the script. The run script is generated by this method. All
    three sections are put together and written to single file per args.

    Args:
        project_name (str): Name for the particular run of the job.
        numtasks: Number of tasks to run
    
    Keyword Args:
        filename (str): Name of the generated file. Default: 'script.sh'.
        email (str): Email address to send job output to. If None, batch script
            will not be configured to send email. Default: None.
        datestamps (bool): If True, datestamp the output. Default: False.
        verbose (bool): If True, output wil be verbose. Default: False.
    
    ***FIXME: Function needs to be updated to use modules' setup.py for run
        section.
    """
    logger = logging.getLogger('onramp')
    logger.debug('PCE.tools._build_SGE_script() called')
    contents = '#!/bin/bash\n'
    contents += '###################################\n'
    contents += '# SGE Submission options\n'
    contents += '#\n'
    contents += '# Name of the job\n'
    contents += '#$ -N ' + project_name + '\n'
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

    if datestamps:
        logger.debug('%s configured for datestamps' % project_name)
        contents += 'date\n'

    # FIXME: This needs to be communicated to CWD/setup.py:
    #if verbose:
    #    v = ' -v'
    #else:
    #    v = ''

    contents += 'mpirun' + v + ' -np ' + str(np)
    contents += ' ' + project_name + '.c-mpi' + '\n'

    if datestamps:
        contents += 'date\n'

    contents += '\n'
    if email:
        logger.debug('%s configured for email reporting to %s'
                     % (project_name, email))
        contents += '#$ -m be\n'
        contents += '#$ -M ' + email + '\n'

    script_file = open(filename, 'w')
    script_file.write(contents)
    script_file.close()
    logger.info('SGE script written for %s' % project_name)


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
