# OnRamp Documentation

This directory contains documentation targeted at various users of OnRamp, and contributors to the project.

For a Quick Start Guide see the [README](../README.md) in the base directory.


--------------------------
## OnRamp User Role

Editing: The OnRamp project is an interactive web portal that allows you to launch parallel applications and explore 
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
     * __NOTE: Most of the above will need to be updated when SSL/HTTPS implemented__

 * Specific tips for 

--------------------------
## Curriculum Module Writers

To be written...

 * Include description of the various scripts
 * Include discussion of thing to watch out for while developing a module

--------------------------
## Contributing Developers

To be written...
 * Include information about debugging and testing
 * Adding new PCE targets
 * Working with Module and Job State
 * Adding new bin/onramp_pce_service.py commands
 * PCE.tools pydoc

### Currently Implemented REST Interface:
| URL                       | GET                                        | POST               | DELETE             |
|---------------------------|--------------------------------------------|--------------------|--------------------|
| modules/                  | Get list of modules                        | Install new module |                    |
| modules/?state=Available  | Get list of packaged modules               | Install new module |                    |
| modules/MOD_ID/           | Get info/status about particular module    | Deploy module      | Remove module      |
| jobs/                     |                                            | Launch new job     |                    |
| jobs/JOB_ID               | Get status/results for particular job      |                    | Remove job/results |
| cluster/info              | Get cluster attrs/docs/etc.                |                    |                    |
| api/                      | Get enumeration of all endpoints           |                    |                    |

### REST Interface Details:
 * **modules/**
     * **GET** - Return a list of all installed educational modules.
         * Response Fields:
             + **status_code**:
                 + *0*: Success
             + **status_msg** - Indication of result/error
             + **modules** - List of modules on the system at the 'Checkout in progress'
                             state or higher. Each module contains attrs identical to what's
                             returned in *GET modules/MOD_ID/*.

    * **GET modules/?state=Available** - Return a list of all installed educational modules.
        * Response Fields:
            + **status_code**:
                + *0*: Success
            + **status_msg** - Indication of result/error
            + **modules** - List of shipped modules on the system. Each module contains
                            attrs identical to what's returned in *GET modules/MOD_ID/*

    * **POST** - Clone/upload and deploy a new educational module.
        * Required Request Fields:
            + **mod_id**: Id to represent the new module
            + **mod_name**: Human-readable repr of new module (used only for folder
                structure)
            + **source_location**: Dictionary with the following fields:
                + **type**: Indication of URI type. Currently, must be 'local'
                + **path**: URI path
        * Response Fields:
            + **status_code**:
                + *0*: Success
                + *-8*: Invalid request parameters
                + *-9*: Inputspec file not found
            + **status_msg** - Indication of result/error

 * **modules/*MOD_ID*/**
    * **GET** - Return status of module corresponding to MOD_ID.
        *Response Fields:
            + **status_code**:
                + *0*: Success
            + **status_msg** - Indication of result/error
            + **module** - Educational module attrs:
                + *mod_id* - Module ID
                + *mod_name* - Module name
                + *installed_path* - Path module is checked out/installed to
                + *state* - One of: 'Does not exist', 'Available', 'Checkout in progress',
                                    'Checkout failed', 'Installed', 'Deploy in progress',
                                    'Deploy failed', 'Module ready', 'Admin required'
                + *error* - Detailed explanation of state if applicable/necessary
                + *source_location* - Location module was checked out from
                    + *type* - Currently must be 'local'
                    + *path* - Path to resource at source location
                + *uioptions* - Dict representation of module's config/onramp_uioptions.spec file

    * **POST** - Deploy the indicated module.
        * Response Fields:
            + **status_code**:
                + *0*: Success
                + *-2*: Module not installed
                + *-8*: Invalid module ID
            + **status_msg** - Indication of result/error
    * **DELETE** - Delete the specified educational module.
        * Response Fields:
            + **status_code**:
                + *0*: Success
            + **status_msg** - Indication of result/error

 * **jobs/**
    * **POST** - Launch a new job.
        * Required Request Fields:
            + **username**: Username of user submitting job
            + **mod_id**: Id of module to be run
            + **job_id**: Id to represent the new job
            + **run_name**: Human-readable label for job run
        * Response Fields:
            + **status_code**:
                + *0*: Job launched
                + *-8*: Invalid request parameters
                + *-9*: Inputspec file not found
            + **status_msg** - Indication of result/error

 * **jobs/*JOB_ID*/**
    * **GET** - Get status/results/info about particular job.
        * Response Fields:
            + **status_code**:
                + *0*: Success
            + **status_msg** - Indication of result/error
            + **job** - Job attrs:
                + *job_id* - Id for job given by OnRamp
                + *mod_id* - Id for module job is running
                + *username* - Username of user launching job
                + *run_name* - Human-readable identifier for job run
                + *state* - One of: 'Setting up launch', 'Launch failed', 'Preprocessing',
                                    'Preprocess failed', 'Schedule failed', 'Scheduled',
                                    'Queued', 'Run failed', 'Running', 'Postprocessing',
                                    'Done'
                + *error* - Detailed indication of error when applicable/possible
                + *scheduler_job_num* - Id for job given by scheduler
                + *mod_status_output* - Output from bin/onramp_status.py
                + *output* - Contents of output.txt
                + *visible_files* - List of dictionaries corresponding to available visible files with the following fields:
                     + name - Name of the file
                     + size - Size, in bytes, of the file
                     + URL - URL, relative to host:port of the PCE, that the file is available at
    * **DELETE** - Cancel a particular job and/or remove job info.
        * Response Fields:
            + **status_code**:
                + *0*: Success
            + **status_msg** - Indication of result/error

 * **cluster/info**
    * **GET** - Retrieve statically hosted cluster attrs/status/docs/etc.
