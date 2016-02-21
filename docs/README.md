# OnRamp Documentation

This directory contains documentation targeted at various users of OnRamp, and contributors to the project.

For a Quick Start Guide see the [README](../README.md) in the base directory.


--------------------------
## OnRamp User Role

The OnRamp project is an interactive web portal that allows you to launch parallel applications and explore 
system software.  The user friendly interface hides the complexity of the parallel computing environments (PCE) allowing 
you to focus on learning the parallel and distributed computing (PDC) concepts outlined in your modules.  Be sure to 
hover over any highlighted words to view the definition and the role it plays in launching your job in a PCE.  Understanding
these concepts will allow you to fully leverage the power of your PCE.  

Upon a successful login your user dashboard will appear.  Here, you can view a list of recent jobs you have launched
as well as launch new jobs.

To launch a new job:
*Click on the "Let's launch some jobs button," you will be navigated to your workspace.
*Click the button below "I want to pick a PCE" to choose the PCE you will be running on
*Click the button below "I want to pick a module to run" to choose a module that was set up by the admin user
*After setting your runtime parameters, click the "Launch Job!" button.  This will navigate you to the job details
page where you can view the details of your job.
 

--------------------------
## Administrator User Role

To be written...
 * PCE
     * Requirements:
        * python2.7
        * virtualenv
     * Installation
        * bin/onramp_pce_install.py
            * Handling of reinstall
            * Handling of `bin/onramp_pce_config.cfg`
            * Handling of `topo.pdf`
     * Configuration
        * `bin/onramp_pce_config.cfg` fields/options
     * Operation
        * Quickstart on how to start/stop/restart PCE service
        * `bin/onramp_pce_service.py`
            * Docstring and notes for `start`
            * Docstring and notes for `stop`
            * Docstring and notes for `restart`
            * Docstring and notes for `modtest`
            * Docstring and notes for `modinstall`
            * Docstring and notes for `modready`
            * Docstring and notes for `moddelete`
            * Docstring and notes for `joblaunch`
            * Docstring and notes for `jobdelete`
            * Docstring and notes for `shell`
     * Adding additional static files
     * _NOTE: All of the above will need to be updated when SSL/HTTPS implemented_

 * Specific tips for 

--------------------------
## Curriculum Module Writers

To be written...

 * Include description of the various scripts
 * Include discussion of thing to watch out for while developing a module

--------------------------
## Contributing Developers

To be written...

 * Include REST Interface documentation
 * Include information about debugging and testing
