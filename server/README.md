# OnRamp Server

This directory contains the code necessary to setup the OnRamp Server on a publicly accessible web server. The OnRamp Server provides the user accessible front end interface to the OnRamp service.

-------------------------------
## Directory Structure

 * [index.html](index.html) : Home page for the OnRamp Web Service

------------------------
## Temporary Directories

The following directories are automatically created and managed by the OnRamp PCE Service (should never be in the git repository):

 * ```pce``` : Contains documentation from the PCE about that environment. See the ```pce/docs``` directory.
 * ```pce/module``` : Contains documentation about the Curriculum Module deployed on the PCE. 
 * ```users``` : Contains the OnRamp user's working directories. These directories contain temporary files as they move too and from the server. For example, when a job has finished the results from that run may be copied into this temporary location so that the user can download the files through the web service.