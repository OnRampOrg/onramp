PCE Configuration
=================

User-level configuration of the PCE service exists in the onramp/pce/onramp_pce_config.cfg file. The file contains two sections: server and cluster. The following paramaters are used::

    [server]
    socket_host = IP address
    socket_port = Port

    [cluster]
    batch_scheduler = One of: SLURM, PBS, SGE
    log_level = One of: DEBUG, INFO, WARN, ERROR, CRITICAL
    log_file = Absolute or relative to onramp/pce
