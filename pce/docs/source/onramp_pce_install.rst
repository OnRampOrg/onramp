bin/onramp_pce_install.py
===================

This script performs the initial setup of the local PCE environment. This includes construction of required folder structure, initialization of a Python virtual environment using virtualenv, installation of Python dependencies to the virtual environment, and attachment of the PCE package to the virtual environment. The script can also be used to reset an already installed environment to the initial post-setup state. If run after installation has already been accomplished, the user will be prompted with a choice between exiting and reinstalling. If no bin/onramp_pce_config.cfg exists, a default will be installed. If it does exist, the user will be prompted with a choice to keep the current or replace with the default.

.. automodule:: onramp_pce_install

