# OnRamp Project

This is the public repository for the OnRamp to Parallel Computing project.  You will find the source code, documentation and modules for running an instance of the OnRamp Server and an OnRamp Parallel Compute Environment (PCE).

The OnRamp project provides a web portal interface to parallel compute environments (PCEs) so that users can run parallel codes remotely in a structured and familiar environment.  The web portal provides educational material to learn how to navigate a PCE directly using a series of user levels and examples.

## Mailing lists

* [Public User's Mailing List](https://groups.google.com/forum/#!forum/onramp-pdc)
  * A list for the user community to ask questions and share experiences with OnRamp.
  * **Public** discussion and archives
  * Must join the list to post and receive messages
  * Anyone may join
* [Private Developer's Mailing List](https://groups.google.com/forum/#!forum/onramp-pdc-devel)
  * A list for the developer community to coordinate OnRamp development activities.
  * **Private** discussion and archives
  * Must join the list to post and receive messages

## Progress

This project is still being designed and implemented.  We hope to have a first implementation available on github by then end of the year 2015.


-----------------------------------
## Quick Start Guide

There are two software services in OnRamp.

 * **Parallel Computing Environment (PCE)** - The HPC system that you wish to expose as a running environment.
 * **OnRamp Server** - The server used to host the website and marshall activities to the backend PCEs.

### Setup a PCE

Start by setting up a PCE environment.

 1. Checkout the repository on the PCE.

  ```
$$ git checkout https://github.com/ssfoley/onramp.git onramp
  ```
 1. Run the setup script. 
**Note:** This may take a few minutes as it will download and install the required python packages.

  ```
$$ cd onramp/pce
$$ ./bin/onramp_pce_install.py 
  ```
 1. Configure the OnRamp PCE service.

  ```
$$ $EDITOR bin/onramp_pce_config.cfg
# Follow instructions in the file to customize it for your system.
# Let's assume you are running on 127.0.0.1 port 9091
  ```
 1. Start the OnRamp PCE service. It runs in the background as a daemon.

  ```
$$ bin/onramp_pce_service.py start
Starting REST server...
$$
  ```
 1. Confirm that the OnRamp PCE service is running.

  ```
$$ curl -I http://127.0.0.1:9091/cluster/ping
HTTP/1.1 200 OK
$$ 
  ```

### Setup the OnRamp Server

Now setup the OnRamp Server. This can be on the same machine as the PCE, but we recommend putting it on a separate web server so that there is a logical separation from the OnRamp Server service and the range of OnRamp PCEs that are available.

 1. Checkout the repository on the server. **Note:** If you are running the OnRamp Server and OnRamp PCE on the same machine you can use the same repository from above - so skip this step.

  ```
$$ git checkout https://github.com/ssfoley/onramp.git onramp
  ```
 1. Run the setup script. 
**Note:** This may take a few minutes as it will download and install the required python packages.

  ```
$$ cd onramp/server
$$ ./bin/onramp_server_install.py 
  ```
 1. Configure the OnRamp Server service.

  ```
$$ $EDITOR bin/onramp_server_config.cfg
# Follow instructions in the file to customize it for your system.
# Let's assume you are running on 127.0.0.1 port 9092
$$
$$ $EDITOR .htaccess
# Change the RewriteRule to match the host and port that you specified above
  ```
 1. Start the OnRamp Server service. It runs in the background as a daemon.

  ```
$$ ./bin/onramp_server_service.py start
Starting REST server...
$$
  ```
 1. Confirm the OnRamp Server service is running.

  ```
$$ curl http://127.0.0.1:9092/
OnRamp Server is running...
$$ 
  ```
 1. Expose the web service. Here we assume you have a ```www``` directory in your home directory, but this can be anywhere that is web accessible. 

  ```
$$ cd ~/www
$$ ln -s $HOME/onramp/server onramp
  ```
 1. Confirm the OnRamp Server service is exposed.

  ```
$$ curl http://www.mydomain.edu/~username/onramp/api
OnRamp Server is running... 
$$ curl -I http://www.mydomain.edu/~username/onramp/
HTTP/1.1 200 OK
...
$$
  ```
 1. Open a webpage to the URL and you should see the welcome page:
  * OnRamp Server Homepage: `http://www.mydomain.edu/~username/onramp/`
  * OnRamp Server API: `http://www.mydomain.edu/~username/onramp/api/`


### Connect the OnRamp Server with the OnRamp PCE

To be written...
