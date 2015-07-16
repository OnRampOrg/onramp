#!../env/bin/python

import os
import sys
from subprocess import check_output

def fail_deployment(mod_state=None, msg=None):
    if mod_state:
        mod_state['status'] = 'deploy failed'
        if msg:
            mod_state['error'] = msg
        save_module_state(mod_state)
    if msg:
        sys.stderr.write(msg)
    sys.exit(-1)
    
def deploy_module(mod_id):
    mod_state = load_module_state(mod_id)

    if not mod_state:
        fail_deployment(mod_state={'mod_id':mod_id},
                        msg='Corrupted state for module %d' % mod_id)

    if mod_state['status'] != 'not deployed':
        msg = 'Module %d not in a deployable state' % mod_id
        fail_deployment(mod_state=mod_state, msg=msg)

    if not os.path.isdir(mod_state['installed_path']):
        fail_deployment(mod_state=mod_state,
                        msg=('Module %d does not exist at location given'
                            'by installed_path param'))

    mod_state['status'] = 'deploy in progress'
    save_module_state(mod_state)
    ret_dir = os.cwd()
    os.chdir(mod_state['installed_path'])

    try:
        check_output(['../../src/env/python', 'bin/onramp_deploy'])
    except CalledProcessError as e:
        if e.returncode != 1:
            msg = ('bin/onramp_deploy.py returned invalid exit status: %d'
                   % e.returncode)
            fail_deployment(mod_state=mod_state, msg=msg)
        mod_state['status'] = 'admin required'
        mod_state['error'] = e.output
        save_module_state(mod_state)
        sys.exit(0)

    mod_state['status'] = 'module ready'
    save_module_state(mod_state)
    sys.exit(0)
