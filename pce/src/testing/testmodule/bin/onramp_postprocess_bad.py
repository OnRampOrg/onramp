#!/usr/bin/env python

#
# Curriculum Module Preprocess Script
# - Run once per run of the module by a user
# - Run before job submission. So -not- in an allocation.
# - onramp_run_params.cfg file is available in current working directory
#
import sys
import time

print 'This is an output log test.'
sys.stderr.write('Output to stderr')

# No postprocessing required
time.sleep(10)


# Exit 0 if all is ok
sys.exit(-1)
# Exit with a negative value if there was a problem
#sys.exit(-1)
