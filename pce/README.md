# Parallel Computing Environment (PCE)

This directory contains the code necessary to setup a new OnRamp Parallel Computing Environment that will connect to an OnRamp Server.


## Directory Structure

 * [onramp\_pce\_config.ini](onramp_pce_config.ini) : PCE configuration file (Uses Python [configobj](https://configobj.readthedocs.org/en/latest/) syntax)
 * [onramp\_pce\_service.py](onramp_pce_service.py) : Provides start/stop/restart/status options to control the OnRamp daemon running on the PCE.
 
	```
	// Start the OnRamp PCE Service
 	$ python onramp_pce_service.py start
	```
	```
 	// Stop the OnRamp PCE Service
 	$ python onramp_pce_service.py stop
	```
	```
 	// Restart the OnRamp PCE Service
 	$ python onramp_pce_service.py restart
	```
	```
 	// Check the status of the OnRamp PCE Service
 	$ python onramp_pce_service.py status
 	```
 	
 * [onramp\_pce\_setup.sh](onramp_pce_setup.sh) : A one-time setup script that will assist the user with deploying the OnRamp PCE Service on a new machine.

	```
	// Setup the OnRamp PCE Service on this PCE
 	$ ./onramp_pce_setup.sh
	```
	
 * [docs](docs/) : Documentation about the PCE that should be provided to the OnRamp users.
 * [src](src/) : Source files to support the OnRamp PCE Service.

------------------------
## Temporary Directories

The following directories are automatically created and managed by the OnRamp PCE Service (should never be in the git repository):

 * ```modules``` : Contains the **deployed** curriculum modules for the PCE.
 * ```users``` : Contains the OnRamp user's working directories.