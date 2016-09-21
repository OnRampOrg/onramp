#!/usr/bin/env python

#
# Curriculum Module Preprocess Script
# - Run once per run of the module by a user
# - Run before job submission. So -not- in an allocation.
# - onramp_run_params.cfg file is available in current working directory
#
import sys
import time
from configobj import ConfigObj, flatten_errors
from validate import Validator, ValidateError, is_integer

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

print 'This is an output log test.'
sys.stderr.write('Output to stderr')

time.sleep(10)


# Nothing else to do for this module


# Exit 0 if all is ok
sys.exit(0)
# Exit with a negative value if there was a problem
#sys.exit(-1)
