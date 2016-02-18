# Template OnRamp Curriculum Module

This is a template curriculum module that lays out a framework for future curriculum module writers.

---------------------
## Configuration

The ```config``` directory contains a series of configuration files, described below. The syntax for these files is in Python [configobj](https://configobj.readthedocs.org/en/latest/#) format.

 * ```config/onramp_metadata.cfg``` : Metadata information about your curriculum module (e.g., Author, Title, Description).
 * ```config/onramp.cfg``` : Any setup/deployment requirements that OnRamp needs to be aware of when using your module.
 * ```config/onramp_uioptions.cfgspec``` : User interaction configuration. This file describes how the end user will interact with your curriculum module. Written in [configspec](https://configobj.readthedocs.org/en/latest/configobj.html#validation). Descriptions of the keys (if needed) can be listed in the ```config/onramp_metadata.cfg``` file.
  * List of files to make visible after the run (regular expressions allowed)
  * List of web form parameters (e.g., block size, number of steps) that change the behavior of the application run. Additional validation criteria should be specified (see the section on [configspec](https://configobj.readthedocs.org/en/latest/configobj.html#validation) in the ```configobj``` documentation)
  	 * This will become a submission form on the web interface which will validate the input parameters before sending the resulting key/value pairs to the ```onramp_*``` scripts for this curriculum module. The file returned from the server will be a configobj file named ```onramp_runparams.cfg```.

---------------------
## Documentation

The ```docs``` directory contains documentation to copy to the OnRamp Server after deploying the module on the PCE. This can be instructions on how to interact with the curriculum module, videos/images related to the content, auto-generated documenation of the source (e.g., [Sphinx](http://sphinx-doc.org/)), or anything else that can be served in a web accessible format. Your ```docs``` directory may reference the ```src``` directory and the CSS in the OnRamp server, if necessary.

OnRamp will cache a copy of this subdirectory on the OnRamp server after module deployment.

---------------------
## Source

The ```src``` directory contains all of the source code for your project. You have complete flexibility over the contents of this directory and its structure.

---------------------
## Reserved Directories/Files

The following paths in the modules's root directory will be written to by the OnRamp PCE service and are, thus, reserved:

 * ```output.txt``` :
 Job output will be written here upon job completion.

 * ```script.sh``` :
 The PCE-generated batch script will be written here at launch.

 * ```onramp_runparams.cfg``` :
 User submitted values for config options defined in ```config/onramp_uioptions.cfgspec``` will be written here at launch.

 * ```.onramp/``` :
 Used by the PCE service to maintain state between HTTP requests.

 * ```log/onramp*``` :
 PCE-gernerated log files will be named as such. NOTE: The ```log/``` folder is available (and recommended) for any log files desired by the module-writer, but the names of those files cannot start with 'onramp'.

---------------------
## Required Supporting Scripts

The ```bin``` directory contains a few OnRamp support scripts that you will need to complete for your curriculum module. They are activated and used at different times in the life-cycle of a curriculum module. Each script will be executed with the module's root directory as the current working directory.

 * **One-Time Module Deployment on a PCE**
   * ```bin/onramp_deploy.py``` : 
   Used by the administrator to **deploy** the curriculum module on the PCE.

   > Provides the module writer an opportunity to do any one-time setup necessary such as compiling software and maybe documentation related to the software.
   >
   > Ideally, all of the necessary setup/installation of the curriculum module occurs in this script. Then after the script completes it will return ```0``` indicating that the module is **Ready for use**.
   >
   >However, it is possible that the administrator will need to perform some manual setup after the ```bin/onramp_deploy.py``` script has completed. In this case the script should return ```1``` after displaying instructions to relay back to the administrator describing the further actions required (instructions should be enclosed in ```<admin></admin>``` tags and may be HTML formatted). For example, the module might need the administrator to update a library path in the ```Makefile``` to complete the build. The module writer may describe those instructions in the output message, or just refer the administrator to a document in the ```docs``` directory of the module.

 * **Launching the Module on the PCE**
   * ```bin/onramp_preprocess.py``` : 
   Called during the **launch** of the curriculum module on the PCE on behalf of the OnRamp user. Called **before job submission** during the setup of the launch script outside of the job allocation.

   > Provides the module writer an opportunity to perform some actions before the job is submitted to the queue. For example, this might involve a custom build of the software, or creation/setup of the input files.
   >
   >The module writer can assume that the script is running on the head node and not in the job allocation. The module writer can also assume that the user configuration options (specified by the user on the OnRamp web server) are available in the ```config``` directory.

  * ```bin/onramp_run.py``` :
   Called during the **launch** of the curriculum module on the PCE on behalf of the OnRamp user. Called **inside the batch script** in the job allocation.

   > Provides the module writer an opportunity to run their module in the batch submission script. They can perform multiple actions, if necessary.
   > 
   > The module writer can assume that the script is running in the job allocation. The module writer can also assume that the user configuration options (specified by the user on the OnRamp web server) are available in the ```config``` directory.
     
  * ```bin/onramp_postprocess.py``` :
   Called during the **results check** of the curriculum module on the PCE on behalf of the OnRamp user. Called **after job completion** outside of the job allocation.

   > Provides the module writer an opportunity to perform some actions after the job has completed. For example, this might involve post-processing of output files, or cleanup of temporary files.
   >
   > The module writer can assume that the script is running on the head node and not in the job allocation. The module writer can also assume that the user configuration options (specified by the user on the OnRamp web server) are available in the ```config``` directory.

  * ```bin/onramp_status.py``` :
   Called during the **results check** of the curriculum module on the PCE on behalf of the OnRamp user. Called **after job submission** outside of the job allocation.

   > Provides the module writer an opportunity to relay additional progress information to the waiting user. For example, this might involve looking at the output files to determine that the application is on ```Step 100 of 1000``` and send that additional progress information back to the user. Anything that this script displays to ```stdout``` will be appended to the status message seen by the user in the web interface.
   > 
   > The module writer can assume that the script is running on the head node and not in the job allocation. The module writer can also assume that the user configuration options (specified by the user on the OnRamp web server) are available in the ```config``` directory. This script will only be called once the job has entered the *running* state in the job queue. It is possible that the script is activated after the job has completed, although a best effort is taken by the OnRamp service to only call the script while *running* on the PCE.
