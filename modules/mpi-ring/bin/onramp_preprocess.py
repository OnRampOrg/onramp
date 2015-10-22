#!/usr/bin/env python

#
# Curriculum Module Preprocess Script
# - Run once per run of the module by a user
# - Run before job submission. So -not- in an allocation.
# - onramp_run_params.cfg file is available in current working directory
#
import os
import sys
from configobj import ConfigObj, flatten_errors
from validate import Validator, ValidateError, is_integer
from subprocess import call, check_call, CalledProcessError

#
# Validate the configobj file we received from the server
# Note: The OnRamp server already does this for you, so you can trust
#       the validity of the file.
#
# This will always be the name of the file, so fine to hardcode here
conf_file = "onramp_runparams.cfg"

config    = ConfigObj(conf_file, configspec="config/onramp_uioptions.cfgspec")
validator = Validator()
results   = config.validate(validator, preserve_errors=True)
if results != True:
    print "Configuration file validation failed!"
    for entry in flatten_errors(config, results):
        section_list, key, error = entry
        if key is not None:
            section_list.append(key)
        else:
            section_list.append("[missing section]")
        section_str = ', '.join(section_list)
        if error == False:
            error = "Missing value or section."
        print section_str, ' = ', error

    sys.exit(-11)


#
# Compile the ring program for each run
# - Note we could do this in the deploy script, just once, but this provides
#   another example of how to do it.
#

#
# Change to the 'src' directory
#
os.chdir('src')
#
# Make the program
#
try:
    rtn = check_call("make")
except CalledProcessError as e:
    print "Error: %s" % e
    sys.exit(-1)


# Exit 0 if all is ok
sys.exit(0)
# Exit with a negative value if there was a problem
#sys.exit(-1)
