#!../env/bin/python
""" Testing for the OnRamp Server
 Usage: 
   $$ cd onramp/server/src/test
   $$ ./testing.py CONFIG_FILE COMMAND

 Commands:
   all        : Run all stages (in order seen below, except 'disconnect' which is run last)

 Admin Commands:
   setup      : Setup the PCE
   connect    : Test connection to PCE
   deploy     : Deploy the module
   disconnect : Disconnect from the PCE

 User Commands:
   run        : Run the module
   status     : Check status of the run
   results    : Get results from the run
   runfiles   : Get files that resulted from the run
"""

#
# Steps for testing
#
# - Admin
#   - Setup the PCE (establish connection/authorization)
#   - Connect to the PCE (Opens the connection)
#   - Deploy Module
#     - Push the Module information
#     - Get the Module doc, and onramp_uioptions.cfgspec file
# - User
#   - Configure and Run the module
#   - Check status of the job
#   - Get Results from this run
#   - Get files associated with this run
#
#

import os
import sys
from pprint import pprint

from configobj import ConfigObj
from OnRampServer import onramppce

######################################################
def _display_header(str):
    print "=" * 70
    print "Running: %s" % str
    print "=" * 70
######################################################
def _setup(conf):
    _display_header("Setup PCE")

    pprint( onramppce.list_all_pces() )

######################################################
def _connect(conf):
    _display_header("Check PCE Connection")
    print "Not Implemented"

######################################################
def _disconnect(conf):
    _display_header("Disconnect from PCE")
    print "Not Implemented"

######################################################
def _deploy(conf):
    _display_header("Deploy Module to PCE")
    print "Not Implemented"

######################################################
def _run(conf):
    _display_header("Run Module on PCE")
    print "Not Implemented"

######################################################
def _status(conf):
    _display_header("Check Job Status")
    print "Not Implemented"

######################################################
def _results(conf):
    _display_header("Gather Job Results")
    print "Not Implemented"

######################################################
def _runfiles(conf):
    _display_header("Gather Job Runtime Files")
    print "Not Implemented"


######################################################
def _all(conf):
    print "=*" * 35
    print "Running: All stages"
    print "=*" * 35
    print ""

    ordered = [_setup,
               _connect,
               _deploy,
               _run,
               _status,
               _results,
               _runfiles,
               _disconnect]
    for key in ordered:
        key(conf)
        print ""

switch = {
    'all': _all,
    'setup': _setup,
    'connect': _connect,
    'disconnect': _disconnect,
    'deploy': _deploy,
    'run': _run,
    'status': _status,
    'results': _results,
    'runfiles': _runfiles
}

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print __doc__

    try:
        conf = ConfigObj( sys.argv[1] )
        pprint( conf, indent=1, width=20 )

        switch[sys.argv[2]](conf)
    except (IndexError, KeyError):
        print __doc__

