"""Service classes encapsulating onramp REST server functionality under HTTP
methods.

Exports:
    Service: Upload, launch, and get status of parallel jobs.
    PrebuiltLaunch: Launch a prebuilt parallel job.
    Request: Get results from previously run parallel jobs.
    ClusterDetails: Cluster attrs, status, etc.
    UserSetup: Create new users.
    Login: Authenticate users.
"""

import copy
import glob
import logging
import os
import json
import hashlib
import shutil
from multiprocessing import Process
from subprocess import call

from Crypto import Random
from Crypto.Cipher import AES

from tools import admin_authenticate, authenticate, decrypt, encrypt, launch_job


def _auth_required(f):
    """Decorator to perform authentication prior to execution of decorated
    function.

    Args:
        f (func): Function requiring an authenticated user.

    NOTE: Raises KeyError if 'username' or 'password' are missing from kwargs.
    """
    def inner(self, *args, **kwargs):
        path = os.path.dirname(os.path.abspath(__file__)) + '/../..'
        base_dir = path + '/users/' + kwargs['username']
        self._logger.debug('Authenticating user: %s' % kwargs['username'])
        auth_response = authenticate(base_dir, kwargs['username'],
                                     kwargs['password'])
        if auth_response:
            self._logger.warning('Failed auth_response: %s' % auth_response)
            return auth_response

        return f(self, *args, **kwargs)
    return inner


def _admin_auth_required(f):
    """Decorator to perform authentication of admin user prior to execution of
    decorated function.

    Args:
        f (func): Function requiring an authenticated admin user.

    NOTE: Raises KeyError if 'username' or 'password' are missing from kwargs.
    """
    def inner(self, *args, **kwargs):
        path = os.path.dirname(os.path.abspath(__file__)) + '/../..'
        base_dir = path + '/users/' + kwargs['adminUsername']
        self._logger.debug('Authenticating admin user: %s'
                           % kwargs['adminUsername'])
        auth_response = admin_authenticate(base_dir, kwargs['adminUsername'],
                                           kwargs['adminPassword'])
        if auth_response:
            self._logger.warning('Failed admin auth_response: %s'
                                 % auth_response)
            return auth_response

        return f(self, *args, **kwargs)
    return inner


class _PCEResourceBase:
    """Provide functionality needed by all PCE resource dispatchers.

    Class Attrs:
        exposed (bool): If True, resource is accessible via the Web.

    Instance Attrs
        conf (ConfigObj): Application config object.
        logger (logging.Logger): Pre-configured application logging instance.
        api_root (str): URL of application's api root.
        url_base (str): Base URL for the resource.

    Methods:
        JSON_response: Constructs JSON reponse from default and provided attrs.
    """
    exposed = True

    def __init__(self, conf):
        """Instantiate PCE Resource.

        Args:
            conf (ConfigObj): Application configuration object.
        """
        self.conf = conf
        self.logger = logging.getLogger('onramp')
        self.url_base = (conf['server']['socket_host'] + ':'
                          + str(conf['server']['socket_port'])
                          + '/' + self.__class__.__name__.lower() + '/')
        self.api_root = (conf['server']['socket_host'] + ':'
                         + str(conf['server']['socket_port'])
                         + '/api/')

    def JSON_response(self, status_code=0, status_msg='Success', **kwargs):
        """Construct JSON response from default and provided attrs.

        Kwargs:
            status_code (int): Status code of response.
            status_msg (str): Status message.
            **kwargs (dict): Key/value pairs to include in the JSON response.
        """
        retval = {}
        retval['status_code'] = status_code
        retval['status_msg'] = status_msg
        retval['url'] = self._build_url()
        retval['api_root'] = self.api_root
        retval.update(kwargs)
        return json.dumps(retval)


class Modules(_PCEResourceBase):
    """Provide API for PCE educational modules resource.
    
    Methods:
        GET: Returns list of installed PCE educational modules.
    """
    def GET(self, **kwargs):
        """Return list of installed PCE educational modules."""
        self.logger.debug('Modules.GET() called')

        path = os.path.dirname(os.path.abspath(__file__)) + '/../../modules'
        if not os.path.isdir(path):
            msg = 'Modules root folder does not exist'
            self.logger.error(msg)
            return self.JSON_response(status_code=-1, status_msg=msg)

        modules = {
            name: {'url': self._build_url(module=name)}
            for name in os.listdir(path)
        }

        self.logger.debug('Returning list of modules')
        return self.JSON_response(modules=modules)

    def _build_url(self, module=None):
        """Return URL for given module, or module base.
        
        Kwargs:
            module (str): Name of module to provide URL for. If 'None', returns
                base URL for modules resource. DEFAULT: None.
        """
        if module:
            return self.url_base + module + '/'
        return self.url_base
