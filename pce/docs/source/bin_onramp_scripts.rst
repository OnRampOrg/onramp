Notes on the Execution of bin/onramp_*.py Scripts
=================================================

An OnRamp educational module provides several scripts to control the setup/execution of the module and to prepare input to the job and output to the user. These scripts may be long-running, thus, should be launched in separate threads or processes to allow the launching thread of execution to complete and return results back to a user.

Output from these scripts (both STDOUT and STDERR) is logged to the to the log/onramp_*.log files in the running module's folder. Successive runs of the scripts overwrite any existing logged output.
