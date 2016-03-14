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

    Returns:
        Tuple consisting of error code and either the requested file if no error
        or string indicating cause of error.
    """
    num_parent_dirs = 3
    if len(dirs) <= num_parent_dirs or '..' in dirs:
        return (-4, 'Bad request')

    run_dir = os.path.join(os.path.join(pce_root, 'users'),
                           '/'.join(dirs[:num_parent_dirs]))
    filename = os.path.join(run_dir, '/'.join(dirs[num_parent_dirs:]))

    cfg_file = os.path.join(run_dir, 'config/onramp_metadata.cfg')
    try:
        conf = ConfigObj(cfg_file, file_error=True)
    except (IOError, SyntaxError):
        return (-3, 'Badly formed or non-existant config/onramp_metadata.cfg') 

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
