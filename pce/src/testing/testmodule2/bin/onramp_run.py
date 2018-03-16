#!/usr/bin/env python

#
# Curriculum Module Run Script
# - Run once per run of the module by a user
# - Run inside job submission. So in an allocation.
# - onramp_run_params.cfg file is available in current working directory
#
import os
import sys
import time
from subprocess import call
from configobj import ConfigObj

config = {
    'onramp': {'np': '4'},
    'hello': {'name': 'hello'}
}

#
# Run my program
#
os.chdir('src')
call(['mpirun', '-np', config['onramp']['np'], 'hello', config['hello']['name']])

# Exit 0 if all is ok
sys.exit(0)
# Exit with a negative value if there was a problem
#sys.exit(-1)
