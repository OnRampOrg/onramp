#!/usr/bin/env python

#
# Curriculum Module Run Script
# - Run once per run of the module by a user
# - Run inside job submission. So in an allocation.
# - onramp_run_params.cfg file is available in current working directory
#
import os
import sys
from subprocess import call, CalledProcessError, check_call
from configobj import ConfigObj

#
# Read the configobj values
#
# This will always be the name of the file, so fine to hardcode here
conf_file = "onramp_runparams.cfg"
# Already validated the file in our onramp_preprocess.py script - no need to do it again
config    = ConfigObj(conf_file)
time = '/usr/bin/time'

#
# Run my program
#
os.chdir('src')

# Retrive mode
mode = config['AUC']['mode']

# Call functions
def default_case():
	print 'Mode option ' + mode + ' invalid.\n'
	sys.exit(-1)

def serial():
	call([time, '-p', './AUC-serial', '-n', config['AUC']['rectangles']])

def openmp():
	call([time, '-p', './AUC-openmp', '-n', config['AUC']['rectangles'], '-t', config['AUC']['threads']])

def mpi():
	call([time, '-p', 'mpirun', '-np', config['onramp']['np'], 'AUC-mpi', '-n', config['AUC']['rectangles']])

def hybrid():
	call([time, '-p', 'mpirun', '-np', config['onramp']['np'], 'AUC-hybrid', '-n', config['AUC']['rectangles'], '-t', config['AUC']['threads']])

# Set options
executables = { 's' : serial, 'o' : openmp, 'm' : mpi, 'h' : hybrid }

# Execute
executables.get(mode, default_case)()

# Exit 0 if all is ok
sys.exit(0)
# Exit with a negative value if there was a problem
#sys.exit(-1)
