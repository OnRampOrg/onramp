bin/onramp_pce_service.py
=====================

The onramp_pce_setup.py script is used to control the PCE service and to provide a means of administering PCE resources via command-line. Additional commands give the ability to test an OnRamp educational module independent of the running PCE service and the ability to launch a Python interpreter with the exact environment used by the PCE service.

To add additional commands:
The file contains a dictionary titled 'switch'. This dict maps commands to handlers. To add a new command, simply define the handler and add the command/handler-name pair to the switch dictionary. If the handler needs to make use of command-line arguments, sys.argv[2:] will yield the list of given args.

.. automodule:: onramp_pce_service
