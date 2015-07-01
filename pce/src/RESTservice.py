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

from PCE.dispatchers import Service, Login, PrebuiltLaunch, Request, \
                            ClusterDetails, UserSetup, Modules


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
    # onramp_config.ini.
    cherrypy.engine.restart()
    logger.debug('Blocking cherrypy engine')
    cherrypy.engine.block()

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.realpath(__file__))

    # Default conf. Some of these can/will be overrided by attrs in
    # onramp_config.ini.
    conf = {
        'global': {
            'server.socket_host': socket.gethostbyname(socket.gethostname()),
            'log.access_file': '../log/access.log',
            'log.error_file': '../log/cherrypy_error.log',
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
            'PIDfile': script_dir + '/.onrampRESTservice.pid',
            'log_level': 'INFO',
            'onramp_log_file': '../log/onramp.log'
        }
    }

    # Load onramp_config.ini and integrate appropriate attrs into cherrpy conf.
    ini = ConfigObj('../onramp_pce_config.ini',
                    configspec='onramp_config.inispec')
    ini.validate(Validator())
    if 'server' in ini.keys():
        for k in ini['server']:
            conf['global']['server.' + k] = ini['server'][k]
    if 'cluster' in ini.keys():
        if 'log_level' in ini['cluster'].keys():
            conf['internal']['log_level'] = ini['cluster']['log_level']
        if 'log_file' in ini['cluster'].keys():
            log_file = ini['cluster']['log_file']
            if not log_file.startswith('/'):
                # Path is relative to onramp_config.ini location
                log_file = '../' + ini['cluster']['log_file']
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
    logger = logging.getLogger('onramp')
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
    cherrypy.tree.mount(Service(ini), '/parallellaunch/service', conf)
    cherrypy.tree.mount(Login(ini), '/parallellaunch/login', conf)
    cherrypy.tree.mount(PrebuiltLaunch(ini), '/parallellaunch/prebuiltlaunch', conf)
    cherrypy.tree.mount(Request(ini), '/parallellaunch/request', conf)
    cherrypy.tree.mount(ClusterDetails(ini), '/parallellaunch/clusterdetails', conf)
    cherrypy.tree.mount(UserSetup(ini), '/parallellaunch/usersetup', conf)
    cherrypy.tree.mount(Modules(ini), '/modules', conf)

    logger.info('Starting cherrypy engine')
    cherrypy.engine.start()
    logger.debug('Registering signal handlers')
    signal.signal(signal.SIGTERM, _term_handler)
    signal.signal(signal.SIGHUP, _restart_handler)
    logger.debug('Blocking cherrypy engine')
    cherrypy.engine.block()
