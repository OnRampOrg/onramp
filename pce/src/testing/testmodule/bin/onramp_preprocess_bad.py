#!/usr/bin/env python

#
# Curriculum Module Preprocess Script
# - Run once per run of the module by a user
# - Run before job submission. So -not- in an allocation.
# - onramp_run_params.cfg file is available in current working directory
#
import time

#
# Validate the configobj file we received from the server
# Note: The OnRamp server already does this for you, so you can trust
#       the validity of the file.
#
# This will always be the name of the file, so fine to hardcode here
time.sleep(10)
sys.exit(-1)
