#!/usr/bin/env python

#
# Curriculum Module Deploy Script
# - Run once per PCE by the admin
# - onramp_run_params.cfg file is -not- available
#
import os
import sys
from subprocess import call


#
# Change to the 'src' directory
#
os.chdir('src')


#
# Load any modules for compiling
#   - need to load mpi module on flux
#
try:
    rtn = check_call("module load mpi")
except CalledProcessError as e:
    print "Error loading module.\nError: %s" % e
    sys.exit(-1)


#
# Make the program
#
call(['make'])


#
# Exit 0 if the module is ready to use
#
sys.exit(0)
#
# Exit 1 if the module requires manual setup
#   before returning 1, display the instructions between <admin> tags - see below
#
#print "<admin>"
#print "1) Login to the system"
#print "2) In the 'src' directory, edit the Makefile to point to your installation of BLAS"
#print "3) Run 'make' in the src directory"
#print "</admin>"
#sys.exit(1)
