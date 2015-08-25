"""OnRamp educational module support package.

Provides functionality for installing/deploying educational modules from various
sources, as well as means of setting/storing/updating module state data.

Exports:
    ModState: Encapsulation of module state that avoids race conditions.
    install_module: Installs module on host system.
    get_source_types: Return list of acceptable module source types (local, git,
        etc.).
    deploy_module: Deploy an installed OnRamp educational module.
    get_modules: Return list of tracked modules or single module.
    get_available_modules: Return list of modules shipped with OnRamp.
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
from subprocess import CalledProcessError, check_output

from configobj import ConfigObj

from PCE import pce_root

_mod_state_dir = os.path.join(pce_root, 'src/state/modules')
_shipped_mod_dir = os.path.join(pce_root, '../modules')
_mod_install_dir = os.path.join(pce_root, 'modules')
_installed_states = ['Installed', 'Deploy in progress', 'Deploy failed',
                    'Module ready']
_logger = logging.getLogger('onramp')

class ModState(dict):
    """Provide access to module state in a way that race conditions are avoided.

    ModState() is only intended to be used in combination with the 'with' python
    keyword. State parameters are stored/acessed as dict keys.
    
    Example:

        with ModState(47) as mod_state:
            val = mod_state['key1']
            mod_state['key2'] = 'val2'
    """

    def __init__(self, id):
        """Return initialized ModState instance.

        Method works in get-or-create fashion, that is, if state exists for
        module id, open and return it, else create and return it.

        Args:
            id (int): Id of the module to get/create state for.
        """
        mod_state_file = os.path.join(_mod_state_dir, str(id))

        try:
            # Raises OSError if file cannot be opened in create mode. If no
            # error, lock the file descriptor when opened.
            fd = os.open(mod_state_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            fcntl.flock(fd, fcntl.LOCK_EX)
            self._state_file = os.fdopen(fd, 'w')
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
            # File already exists. Open and lock it.
            self._state_file = open(mod_state_file, 'r+')
            fcntl.lockf(self._state_file, fcntl.LOCK_EX)
            file_contents = self._state_file.read()
            _logger.debug('File contents for %s:' % mod_state_file)
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


def _local_checkout(source_path, install_path):
    """Install module located on host file sys.

    Args:
        source_path (str): Location of root folder of module to be installed.
        install_path (str): Location to install the new module to.
    """
    if not os.path.isdir(source_path):
        return 'Source path %s does not exist' % source_path

    _logger.debug('Source: %s' % source_path)
    _logger.debug('New: %s' % install_path)
    shutil.copytree(source_path, install_path)
    return None
    
source_handlers = {
    'local': _local_checkout
}

def get_source_types():
    """Return list of acceptable module source types (local, git, etc.)."""
    return source_handlers.keys()

def install_module(source_type, source_path, install_parent_folder, mod_id,
                   mod_name, verbose=False):
    """Install OnRamp educational module into environment.

    Args:
        source_type (str): One of PCE.tools.modules.source_handlers.keys().
        source_path (str): Location to checkout/install/download from at source.
        install_parent_folder (str): Folder the requested module should be
            installed under.
        mod_id (int): Unique integer value to assign to installed moduel.
        mod_name (str): Human-readable module name to use in foldername
            generation.

    Kwargs:
        verbose (bool): Controls level of printed output during installation.
    """
    mod_dir = os.path.join(os.path.join(pce_root, install_parent_folder),
                           '%s_%d' % (mod_name, mod_id))
    source_abs_path = os.path.normpath(os.path.abspath(source_path))
    _logger.debug('cwd: %s' % os.getcwd())
    _logger.debug('source_abs_path: %s' % source_abs_path)

    with ModState(mod_id) as mod_state:
        if 'state' in mod_state.keys():
            if mod_state['state'] == 'Checkout in progress':
                return (-1, 'Module %d already undergoing install process'
                            % mod_id)
            if mod_state['state'] in _installed_states:
                return (-1, 'Module %d already installed' % mod_id)

        mod_state['mod_id'] = mod_id
        mod_state['mod_name'] = mod_name
        mod_state['installed_path'] = None
        mod_state['state'] = 'Checkout in progress'
        mod_state['error'] = None
        mod_state['source_location'] = {
            'type': source_type,
            'path': source_abs_path
        }

    # Checkout module.
    result = source_handlers[source_type](source_abs_path, mod_dir)

    if result:
        with ModState(mod_id) as mod_state:
            mod_state['state'] = 'Checkout failed'
            mod_state['error'] = result
        return (-2, result)

    with ModState(mod_id) as mod_state:
        mod_state['state'] = 'Installed'
        mod_state['error'] = None
        mod_state['installed_path'] = mod_dir

    return (0, 'Module %d installed' % mod_id)

def deploy_module(mod_id, verbose=False):
    """Deploy an installed OnRamp educational module.

    Args:
        mod_id (int): Id of the module to be deployed.

    Kwargs:
        verbose (bool): Increases status output if True.
    """
    mod_dir = None
    not_installed_states = ['Available', 'Checkout in Progress',
                            'Checkout failed']

    with ModState(mod_id) as mod_state:
        if ('state' not in mod_state.keys()
            or mod_state['state'] in not_installed_states):
            return (-1, 'Module %d not installed' % mod_id)
        if mod_state['state'] == 'Deploy in progress':
            return (-1, 'Deployment already underway for module %d' % mod_id)
        mod_state['state'] = 'Deploy in progress'
        mod_state['error'] = None
        mod_dir = mod_state['installed_path']

    ret_dir = os.getcwd()
    _logger.debug('ret_dir: %s' % ret_dir)
    os.chdir(mod_dir)

    try:
        _logger.debug('Calling bin/onramp_deploy.py')
        _logger.debug('CWD: %s' % os.getcwd())
        check_output([os.path.join(pce_root, 'src/env/bin/python'),
                      'bin/onramp_deploy.py'])
        _logger.debug('Back from bin/onramp_deploy.py')
    except CalledProcessError as e:
        if e.returncode != 1:
            with ModState(mod_id) as mod_state:
                error = ('bin/onramp_deploy.py returned invalid status %d'
                         % e.returncode)
                _logger.debug(error)
                mod_state['state'] = 'Deploy failed'
                mod_state['error'] = error
            return (-1, error)

        with ModState(mod_id) as mod_state:
            msg = 'Admin required'
            _logger.debug(msg)
            mod_state['state'] = msg
            mod_state['error'] = e.output
            return (1, msg)
    except OSError as e1:
        _logger.debug(e1)
        with ModState(mod_id) as mod_state:
            mod_state['state'] = 'Deploy failed'
            mod_state['error'] = str(e1)
        return (-1, str(e1))
    finally:
        _logger.debug('finally')
        os.chdir(ret_dir)
        _logger.debug('Back to ret_dir')

    _logger.debug("Updating state to 'Module ready'")
    with ModState(mod_id) as mod_state:
        mod_state['state'] = 'Module ready'
        mod_state['error'] = None

    return (0, 'Module %d ready' % mod_id)

def get_modules(mod_id=None):
    """Return list of tracked modules or single module.

    Kwargs:
        mod_id (int/None): If int, return module resource with corresponding id.
            If None, return list of all tracked module resources.
    """
    if mod_id:
        with ModState(mod_id) as mod_state:
            if 'state' in mod_state.keys():
                mod = copy.deepcopy(mod_state)
                if mod_state['state'] == 'Module ready':
                    uifile = os.path.join(mod_state['installed_path'],
                                          'config/onramp_uioptions.spec')
                    if os.path.isfile(uifile):
                        ui = ConfigObj(uifile)
                        mod['uioptions'] = ui.dict()
                    else:
                        mod['uioptions'] = None
                return mod
        _logger.debug('Mod does not exist at: %s' % time.time())
        return {
            'mod_id': mod_id,
            'mod_name': None,
            'installed_path': None,
            'state': 'Does not exist',
            'error': None,
            'source_location': None
        }

    results = []

    # Need to filter out hidden files because of .nfs* files.
    for id in filter(lambda x: not x.startswith('.'),
                     os.listdir(_mod_state_dir)):
        next_mod = {}
        with ModState(id) as mod_state:
            next_mod = copy.deepcopy(mod_state)
        results.append(next_mod)
    return results

def get_available_modules():
    """Return list of modules shipped with OnRamp."""
    def verify_module_path(x):
        return os.path.isdir(os.path.join(_shipped_mod_dir, x))

    return [{
        'mod_id': None,
        'mod_name': name,
        'installed_path': None,
        'state': 'Available',
        'error': None,
        'source_location': {
            'type': 'local',
            'path': os.path.normpath(os.path.join(_shipped_mod_dir, name))
        }
    } for name in filter(verify_module_path,
                         os.listdir(_shipped_mod_dir))]
