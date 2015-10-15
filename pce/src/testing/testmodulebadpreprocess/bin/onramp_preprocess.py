#!/usr/bin/env python

#
# Curriculum Module Preprocess Script
# - Run once per run of the module by a user
# - Run before job submission. So -not- in an allocation.
# - onramp_run_params.cfg file is available in current working directory
#
import sys

print "We're pretending this is a bad preprocess."
sys.stderr.write('This to stderr')
sys.exit(-1)
