#!../env/bin/python
import argparse
import os
import sys

from PCE.tools import load_module_state

source_types = ['git', 'file']

def install_module(source_type, source_path, install_path, verbose=False):
    

# Build initial folder structure

# Build state object

# Set state to 'checkout in progress'

# Checkout module

# If checkout successful, set state to 'not deployed', else set state to
# 'checkout failed'

# Done

if __name__ == '__main__':
    print head
    sys.exit(0)
    descrip = 'Install an OnRamp educational module from the given location'
    parser = argparse.ArgumentParser(prog='install_module.py',
                                     description=descrip)
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='increase output verbosity')
    parser.add_argument('source_type', choices=source_types,
                        help='the type of resource to install from')
    parser.add_argument('source_path', help='the location of the module')
    help = 'the path to install the module to'
    parser.add_argument('install_path', help=help)
    args = parser.parse_args(args=sys.argv)

    
