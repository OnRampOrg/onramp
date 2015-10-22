#!/usr/bin/env python

#
# Curriculum Module Preprocess Script
# - Run once per run of the module by a user
# - Run before job submission. So -not- in an allocation.
# - onramp_run_params.cfg file is available in current working directory
#
import os
import sys
from subprocess import call, check_call, CalledProcessError

#
# Clean out the binaries
#

#
# Change to the 'src' directory
#
os.chdir('src')
#
# Make the program
#
try:
    rtn = check_call(['make', 'clean'])
except CalledProcessError as e:
    print "Error: %s" % e
    sys.exit(-1)


# Exit 0 if all is ok
sys.exit(0)
# Exit with a negative value if there was a problem
#sys.exit(-1)
