"""Example module test post_deploy_test script.

Any valid python can be here. 'print' anything needed to be seen by test runner.
To signal an error (which will end the module test):
    
    import sys
    sys.exit(error_code)    # Where error_code != 0

Note: Indication of error is not required, that is, if it's desired that the
    module test keeps executing on the discovered error, simply return with
    exit code 0.
"""
import os, sys

print 'deploy_test.py running...'
print os.getcwd()

files = ['bin/onramp_preprocess.py',
         'bin/onramp_run.py',
         'bin/onramp_status.py',
         'bin/onramp_postprocess.py']

for f in files:
    if not os.path.isfile(f):
        print 'Required file missing: %s' % f
        sys.exit(-1)

if os.path.isdir('onramp'):
    print 'Module contents include forbidden dir: onramp/.'
    sys.exit(-1)

print 'deploy_test.py passes.'
