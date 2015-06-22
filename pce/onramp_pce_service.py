#!/usr/bin/env python
"""Control the onramp REST server.

Usage: ./onramp_service.py start|stop|restart
"""

import os
import sys
from subprocess import call
from tempfile import TemporaryFile

_pidfile = '.onrampRESTservice.pid'
_src_dir = 'src'
_script_name = 'RESTservice.py'

def _getPID():
    """Get PID from specified PIDFile.
    
    Returns:
        int: >0 -- RESTservice PID
             -1 -- _pidfile contains invalid PID
             -2 -- _pidfile not found
    """
    pid = 0

    try:
        f = open(_pidfile, 'r')
        pid = int(f.read())
        f.close()
    except IOError as e:
        if e.errno == 2:
            return -2
        raise e
    except ValueError:
        return -1

    # Double check PID from PIDFile:
    outfile = TemporaryFile(mode='w+')
    call(['ps', 'x'], stdout=outfile)
    outfile.seek(0)
    for line in outfile:
        line = line.strip()
        if line.startswith(str(pid)) and line.endswith(_script_name):
            return pid

    return -1

def _start():
    """If not already running, start the REST server."""
    print 'Starting REST server...'
    pid = _getPID()

    if -2 == pid:
        # PIDFile not found, thus, server is not running.
        call(['env/bin/python', 'RESTservice.py'])
        return
    elif -1 == pid:
        print "PIDFile '%s' has been corrupted." % _src_dir + '/' +_pidfile
        return

    print 'Server appears to be already running.'
    return

def _restart():
    """If not stopped, restart the REST server, else start it."""
    print 'Restarting REST server...'
    pid = _getPID()

    if -2 == pid:
        # PIDFile not found, thus, server is not running.
        print 'REST server does not currently appear to be running.'
        _start()
        return
    elif -1 == pid:
        print "PIDFile '%s' has been corrupted." % _src_dir + '/' +_pidfile
        return

    call(['kill', '-1', str(pid)])
    return

def _stop():
    """If running, stop the REST server."""
    print 'Stopping REST server...'
    pid = _getPID()

    if -2 == pid:
        # PIDFile not found, thus, server is not running.
        print 'REST server does not currently appear to be running.'
        return
    elif -1 == pid:
        print "PIDFile '%s' has been corrupted." % _src_dir + '/' +_pidfile
        return

    call(['kill', str(pid)])

switch = {
    'start': _start,
    'restart': _restart,
    'stop': _stop
}

if __name__ == '__main__':
    os.chdir(_src_dir)
    try:
        switch[sys.argv[1]]()
    except (IndexError, KeyError):
        print __doc__
