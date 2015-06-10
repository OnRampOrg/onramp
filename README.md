# OnRamp Project

This is the public repository for the OnRamp to Parallel Computing project.  You will find the source code, documentation and modules for running an instance of the OnRamp server and setting up a parallel compute environment (PCE) it can talk to.

The OnRamp project provides a web portal interface to parallel compute environments so that users can run parallel codes remotely in a structured and familiar environment.  The web portal provides educational material to learn how to navigate a parallel compute environment directly using a series of user levels and examples.

This project is still being designed and implemented.  We hope to have a first implementation available on github by then end of the summer 2015.

-----------------------------------
## Quick Start Guide

There are two software services in OnRamp.

 * **Parallel Computing Environment (PCE)** - The HPC system that you wish to expose as a running environment.
 * **OnRamp Server** - The server used to host the website and marshall activities to the backend PCEs.

### Setup a PCE

Start by setting up a PCE environment.

 * To be written...

### Setup the OnRamp Server

Now setup the OnRamp Server. This can be on the same machine as the PCE, but we recommend putting it on a separate web service so that there is a logical separation from the OnRamp service and the range of PCEs that are available.

 * Checkout the repository on your web server
 * Link the ```onramp/server``` directory to the location on your web server that is publicly accessible.
 * Change the permissions of the directory structure to allow the web server to access the files.
 * ***To be written***
 * Open a webpage to the URL and you should see the welcome page.
