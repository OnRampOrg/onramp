import argparse
import errno
import fcntl
import json
import os
import shutil
import sys

mod_state_dir = 'src/state/modules'
installed_states = ['Installed', 'Deploy in progress', 'Deploy failed',
                    'Module ready']

def _local_checkout(mod_state):
    if not os.path.isdir(mod_state['source_location']['path']):
        return ('Source path %s does not exist'
                 % mod_state['source_location']['path'])

    new_path = os.path.join('modules', '%s_%s'
                            % (mod_state['mod_name'], mod_state['mod_id']))
    shutil.copytree(mod_state['source_location']['path'], new_path)
    return None
    
source_handlers = {
    'local': _local_checkout
}


class ModState(dict):

    def __init__(self, id):
        mod_state_file = os.path.join(mod_state_dir, str(id))

        try:
            fd = os.open(mod_state_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            fcntl.flock(fd, fcntl.LOCK_EX)
            self._state_file = os.fdopen(fd, 'w')
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
            self._state_file = open(mod_state_file, 'r+')
            fcntl.lockf(self._state_file, fcntl.LOCK_EX)
            self.update(json.loads(self._state_file.read()))
            self._state_file.seek(0)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self._close()

    def _close(self):
        self._state_file.write(json.dumps(self))
        self._state_file.truncate()
        self._state_file.close()


def install_module(source_type, source_path, install_parent_folder, mod_id,
                   mod_name, verbose=False):
    
    mod_state_file = os.path.join(mod_state_dir, str(mod_id))
    mod_dir = os.path.join(install_parent_folder, '%s_%d' % (mod_name, mod_id))
    mod_dir = os.path.normpath(os.path.abspath(mod_dir))
    source_abs_path = os.path.normpath(os.path.abspath(source_path))

    with ModState(mod_id) as mod_state:
        if 'state' in mod_state.keys():
            if mod_state['state'] == 'Checkout in progress':
                return (-1, 'Module %d already undergoing install process'
                            % mod_id)
            if mod_state['state'] in installed_states:
                return (-1, 'Module %d already installed' % mod_id)

        mod_state['mod_id'] = mod_id
        mod_state['mod_name'] = mod_name
        mod_state['installed_path'] = mod_dir
        mod_state['state'] = 'Checkout in progress'
        mod_state['error'] = None
        mod_state['source_location'] = {
            'type': source_type,
            'path': source_abs_path
        }

    # Checkout module.
    result = source_handlers[source_type](mod_state)

    if result:
        with ModState(mod_id) as mod_state:
            mod_state['state'] = 'Checkout failed'
            mod_state['error'] = result
        return (-2, msg)

    with ModState(mod_id) as mod_state:
        mod_state['state'] = 'Installed'
        mod_state['installed_path'] = mod_dir

    return (0, 'Module %d installed' % mod_id)

if __name__ == '__main__':
    descrip = 'Install an OnRamp educational module from the given location'
    parser = argparse.ArgumentParser(prog='install_module.py',
                                     description=descrip)
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='increase output verbosity')
    parser.add_argument('source_type', choices=source_handlers.keys(),
                        help='type of resource to install from')
    parser.add_argument('source_path', help='source location of the module')
    parser.add_argument('install_parent_folder',
                        help='parent folder to install module under')
    parser.add_argument('mod_id', help='unique id to give module', type=int)
    parser.add_argument('mod_name', help='name of the module')
    args = parser.parse_args(args=sys.argv[1:])

    result, msg = install_module(args.source_type, args.source_path,
                                 args.install_parent_folder, args.mod_id,
                                 args.mod_name, verbose=args.verbose)

    if result != 0:
        sys.stderr.write(msg + '\n')
    else:
        print msg

    sys.exit(result)
