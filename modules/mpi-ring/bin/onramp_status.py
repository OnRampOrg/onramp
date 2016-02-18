#!/usr/bin/env python

#
# Curriculum Module Status Script
# - Run while the job is running
# - Run -outside- of the allocation
# - onramp_run_params.cfg file is available in current working directory
#
import sys
import re

#
# Display any special message you want the user to see, or leave blank if nothing.
# Please restrict status messages to 1 line of text.
#

# Read in the output file
lines = [line.rstrip('\n') for line in open('output.txt')]

# If the file is empty then nothing to do
if len(lines) <= 0:
    sys.exit(0)


#print "Status) Number of Lines: %d" % len(lines)

# Find the last line of 'Increment value'
last_status = None
for line in lines:
    searchObj = re.search( r'Increment value (.*)', line)
    if searchObj:
        last_status = searchObj.group(1).strip()

if last_status is not None:
    print "%s" % last_status

#
# Exit successfully
#
sys.exit(0)
