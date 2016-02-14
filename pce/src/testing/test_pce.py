#!../env/bin/python
"""A simple test script for the PCE portion of OnRamp.

Usage: ./test_pce.py

This script is only intended to be run in a fresh install of the repository. It
has side-effects that could corrupt module and user data if run in a production
setting.

Prior to running this script, ensure that onramp/pce/bin/onramp_pce_install.py
has been called and that the server is running. Also Ensure
./test_pce_config.cfg contains the proper settings.
"""
import nose
import sys

if __name__ == '__main__':
    print (__doc__)
    response = raw_input('(C)ontinue or (A)bort? ')
    if response != 'C':
        sys.exit(0)

    nose.main()
