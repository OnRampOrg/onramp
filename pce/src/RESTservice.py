#!/usr/bin/env python2.7

"""Initialize and launch the onramp REST server."""

import logging
import os
import signal
import socket
import sys

import cherrypy
from cherrypy.process.plugins import Daemonizer, PIDFile
from configobj import ConfigObj
from validate import Validator

from PCE.dispatchers import APIMap, ClusterInfo, ClusterPing, Files, Jobs, \
                            Modules
from PCEHelper import pce_root


def _CORS():
    """Set HTTP Access Control Header to allow cross-site HTTP requests from
    any origin.
    """
    cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'

def _term_handler(signal, frame):
    """Gracefully shutdown the server and exit.

    This function is intended to be registered as a SIGTERM handler.
    """
    logger = logging.getLogger('onramp')
    logger.info('Shutting down server')

    cherrypy.engine.exit()
    logger.info('Exiting')
    sys.exit(0)

def _restart_handler(signal, frame):
    """Restart the server.

    This function is intended to be registered as a SIGHUP handler.
    """
    logger = logging.getLogger('onramp')
    logger.info('Restarting server')
    # FIXME: This needs to reload the config, including attrs in
    # onramp_pce_config.cfg.
    cherrypy.engine.restart()
    logger.debug('Blocking cherrypy engine')
    cherrypy.engine.block()

if __name__ == '__main__':
    # Default conf. Some of these can/will be overrided by attrs in
    # onramp_pce_config.cfg.
    conf = {
        'global': {
            'server.socket_host': socket.gethostbyname(socket.gethostname()),
            'log.access_file': 'log/access.log',
            'log.error_file': 'log/cherrypy_error.log',
            'log.screen': False,

            # Don't run CherryPy Checker on custom conf sections:
            # FIXME: This setting doesn't seem to be working...
            'checker.check_internal_config': False,
        },

        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.CORS.on': True
        },

        'internal': {
            'PIDfile': os.path.join(os.getcwd(), 'src/.onrampRESTservice.pid'),
            'log_level': 'INFO',
            'onramp_log_file': 'log/onramp.log'
        }
    }

    # Load onramp_pce_config.cfg and integrate appropriate attrs into cherrpy
    # conf.
    cfg = ConfigObj(os.path.join(pce_root, 'bin', 'onramp_pce_config.cfg'),
                    configspec=os.path.join(pce_root, 'src', 'configspecs',
                                            'onramp_pce_config.cfgspec'))
    cfg.validate(Validator())
    if 'server' in cfg.keys():
        for k in cfg['server']:
            conf['global']['server.' + k] = cfg['server'][k]
    if 'cluster' in cfg.keys():
        if 'log_level' in cfg['cluster'].keys():
            conf['internal']['log_level'] = cfg['cluster']['log_level']
        if 'log_file' in cfg['cluster'].keys():
            log_file = cfg['cluster']['log_file']
            if not log_file.startswith('/'):
                # Path is relative to onramp_pce_config.cfg location
                log_file = cfg['cluster']['log_file']
            conf['internal']['onramp_log_file'] = log_file

    cherrypy.config.update(conf)

    # Set up logging.
    log_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    log_name = 'onramp'
    logger = logging.getLogger(log_name)
    logger.setLevel(log_levels[conf['internal']['log_level']])
    handler = logging.FileHandler(conf['internal']['onramp_log_file'])
    handler.setFormatter(
        logging.Formatter('[%(asctime)s] %(levelname)s %(message)s'))
    logger.addHandler(handler)
    logger.info('Logging at %s to %s' % (conf['internal']['log_level'],
                                         conf['internal']['onramp_log_file']))

    # Log the PID
    PIDFile(cherrypy.engine, conf['internal']['PIDfile']).subscribe()

    Daemonizer(cherrypy.engine).subscribe()
    cherrypy.tools.CORS = cherrypy.Tool('before_finalize', _CORS)
    cherrypy.tree.mount(Modules(cfg, log_name), '/modules', conf)
    cherrypy.tree.mount(Jobs(cfg, log_name), '/jobs', conf)
    cherrypy.tree.mount(ClusterInfo(cfg, log_name), '/cluster/info', conf)
    cherrypy.tree.mount(ClusterPing(cfg, log_name), '/cluster/ping', conf)
    cherrypy.tree.mount(Files(cfg, log_name), '/files', conf)
    cherrypy.tree.mount(APIMap(cfg, log_name), '/api', conf)

    logger.info('Starting cherrypy engine')
    cherrypy.engine.start()
    logger.debug('Registering signal handlers')
    signal.signal(signal.SIGTERM, _term_handler)
    signal.signal(signal.SIGHUP, _restart_handler)
    logger.debug('Blocking cherrypy engine')
    cherrypy.engine.block()
