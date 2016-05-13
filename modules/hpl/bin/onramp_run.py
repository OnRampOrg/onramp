#!/usr/bin/env python

#
# Curriculum Module Run Script
# - Run once per run of the module by a user
# - Run inside job submission. So in an allocation.
# - onramp_run_params.cfg file is available in current working directory
#
import os
import sys
from subprocess import call
from configobj import ConfigObj

#
# Read the configobj values
#
# This will always be the name of the file, so fine to hardcode here
conf_file = "onramp_runparams.cfg"
# Already validated the file in our onramp_preprocess.py script - no need to do it again
config    = ConfigObj(conf_file)

#
# Run my program
#
os.chdir('src')

call(['mpirun', 'np', 'parameters', config['hpl']['num_Ns'], config['hpl']['Ns'], config['hpl']['num_NBs'], config['hpl']['NBs'], config['hpl']['num_PsQs'], config['hpl']['Ps'], config['hpl']['Qs']]);

call(['mpirun', 'np', config['onramp']['np'], 'xhpl']);

# Exit 0 if all is ok
sys.exit(0)
