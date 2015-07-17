#!src/env/bin/python
import argparse
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

def fail_install(mod_state=None, msg=None):
    if mod_state:
        mod_state['state'] = 'Checkout failed'
        if msg:
            mod_state['error'] = msg
        save_module_state(mod_state)
    return (-1, msg)

def install_module(source_type, source_path, install_parent_folder, mod_id,
                   mod_name, verbose=False):
    
    mod_state_file = os.path.join(mod_state_dir, str(mod_id))
    mod_dir = os.path.join(install_parent_folder, '%s_%d' % (mod_name, mod_id))
    mod_dir = os.path.normpath(os.path.abspath(mod_dir))
    source_abs_path = os.path.normpath(os.path.abspath(source_path))

    if os.path.exists(mod_state_file):
        mod_state = load_mod_state(mod_id)
        if not mod_state:
            return fail_install(msg='Corrupted state for module %d' % mod_id)
        if mod_state['state'] == 'Checkout in progress':
            return fail_install(msg='Install already under way for module %d'
                                    % mod_id)
        elif mod_state['state'] in installed_states:
            return fail_install(msg='Module %d already installed' % mod_id)
    elif os.path.exists(mod_dir):
        return fail_install(msg='Corrupted state for module %d' % mod_id)

    # Build state object. Set state to 'Checkout in progress'.
    mod_state = {
        'mod_id': mod_id,
        'mod_name': mod_name,
        'source_location': {
            'type': source_type,
            'path': source_abs_path
        },
        'installed_path': mod_dir,
        'state': 'Checkout in progress',
        'error': None
    }

    with open(mod_state_file, 'w') as f:
        f.write(json.dumps(mod_state))

    # Checkout module.
    result = source_handlers[source_type](mod_state)

    if result:
        return fail_install(mod_state=mod_state, msg=result)

    mod_state['status'] = 'Installed'
    mod_state['installed_path'] = mod_dir
    save_module_state(mod_state)
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
        sys.stderr.write(msg)
    else:
        print msg

    sys.exit(result)
