#!/usr/bin/env python

#
# Curriculum Module Deploy Script
# - Run once per PCE by the admin
# - onramp_run_params.cfg file is -not- available
#
import os
import sys
import time
from subprocess import call


#
# Change to the 'src' directory
#
os.chdir('src')
#
# Make the program
#
call(['make'])

#
# Exit 0 if the module is ready to use
#
#sys.exit(0)
#
# Exit 1 if the module requires manual setup
#   before returning 1, display the instructions between <admin> tags - see below
#
print "<admin>"
print "1) Login to the system"
print ("1) From the onramp/pce/ dir, execute ./onramp_pce_service.py modready ",
       "MOD_ID")
print "</admin>"
sys.exit(1)
