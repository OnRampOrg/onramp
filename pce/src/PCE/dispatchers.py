"""Dispatchers implementing the OnRamp PCE API.

Exports:
    Modules: View, add, update, and remove PCE educational modules.
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

import cherrypy
from Crypto import Random
from Crypto.Cipher import AES

from tools import admin_authenticate, authenticate, decrypt, encrypt, launch_job

def required_params(*args):
    """Validate contents of JSON request body.

    *args: Parameters that are required to be provided in the JSON body of the
        request.
    """
    def inner1(f):
        def inner2(self):
            data = cherrypy.request.json
            missing_attrs = filter(lambda x: x not in data.keys(), args)

            if missing_attrs:
                msg = ('The following paramaters were expected but not '
                       'supplied: %s' % ', '.join(missing_attrs))
                self.logger.warn(msg)
                cherrypy.response.status = 400
                return self.JSON_response(status_code=-8, status_msg=msg,
                                  required_params=args)

            self.logger.debug('Request params validated.')
            return f(self, **data)
        return inner2
    return inner1


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
        self.logger.debug('Authenticating user: %s' % kwargs['username'])
        auth_response = authenticate(base_dir, kwargs['username'],
                                     kwargs['password'])
        if auth_response:
            self.logger.warning('Failed auth_response: %s' % auth_response)
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
        self.logger.debug('Authenticating admin user: %s'
                           % kwargs['adminUsername'])
        auth_response = admin_authenticate(base_dir, kwargs['adminUsername'],
                                           kwargs['adminPassword'])
        if auth_response:
            self.logger.warning('Failed admin auth_response: %s'
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
        validate_JSON_request: Validates JSON request data.
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

    def JSON_response(self, id=None, url=True, status_code=0,
                      status_msg='Success', **kwargs):
        """Construct JSON response from default and provided attrs.

        Kwargs:
            id: If not none, set response value for 'url' to the url for
                specific resource specified by id.
            url (bool): If false, set response value for 'url' to None.
            status_code (int): Status code of response.
            status_msg (str): Status message.
            **kwargs (dict): Key/value pairs to include in the JSON response.
        """
        self.logger.debug('KWARGS: %s' % str(kwargs))
        retval = {}
        retval['status_code'] = status_code
        retval['status_msg'] = status_msg
        if url:
            retval['url'] = self._build_url(id=id)
        else:
            retval['url'] = None
        retval['api_root'] = self.api_root
        retval.update(kwargs)
        return json.dumps(retval)


class Jobs(_PCEResourceBase):
    """Provide API for PCE jobs resource.

    Methods:
        POST: Launch a new job.
    """
    @cherrypy.tools.json_in()
    @required_params('module_name', 'run_name', 'username')
    def POST(self, module_name, run_name, username, **kwargs):
        # FIXME: User dir should have been previously created, not created here.
        # Once Users endpoint is implemented, remove creation from here, and
        # test each request to ensure that user dir already exists.

        self.logger.debug('Jobs.POST() called')
        id = '%s_%s' % (username, run_name)
        path = os.path.dirname(os.path.abspath(__file__)) + '/../..'
        user_dir = path + '/users/' + username
        modules_dir = path + '/modules'
        mod_dir = modules_dir + '/' + module_name
        run_dir = user_dir + '/' + run_name
        results_dir = run_dir + '/' + 'Results'

        if not os.path.isdir(modules_dir):
            # FIXME: Should return HTTP status 500.
            msg = 'Modules root folder does not exist'
            self.logger.error(msg)
            return self.JSON_response(status_code=-1, status_msg=msg)
        if not os.path.isdir(mod_dir):
            # FIXME: Should return HTTP status 404.
            msg = 'Module %s does not exist' % module_name
            self.logger.warn(msg)
            return self.JSON_response(status_code=-2, status_msg=msg)
        if os.path.isdir(run_dir):
            # FIXME: Should return HTTP status 400.
            msg = 'A job with this name already exists'
            self.logger.warn(msg)
            return self.JSON_response(id=id, status_code=-3,
                                      status_msg=msg)

        self.logger.info('Making results directory: %s' % results_dir)
        os.makedirs(results_dir, mode=0700)

        self.logger.info('Copying project files from %s to %s'
                         % (mod_dir, run_dir))
        shutil.copytree(mod_dir, run_dir + '/' + module_name)

        # FIXME: ini_params need to be written to
        # run_dir/module_name/onramp_runparams.ini here.

        self.logger.info('Launching job: %s' % id)
        launch_result = launch_job(run_dir + '/' + module_name, id,
                                   self.conf['cluster']['batch_scheduler'])

        # FIXME: Should return 500 for some othe launch_result possibilities.
        return self.JSON_response(id=id, **launch_result)

    def _build_url(self, id=None):
        """Return URL for given module, or module base.
        
        Kwargs:
            module (str): Name of module to provide URL for. If 'None', returns
                base URL for modules resource. DEFAULT: None.
        """
        if id:
            return self.url_base + id + '/'
        return self.url_base


class Modules(_PCEResourceBase):
    """Provide API for PCE educational modules resource.
    
    Methods:
        GET: Returns list of installed PCE educational modules or detail view
            for specific PCE educational module.
    """
    def GET(self, id=None, **kwargs):
        """Return list of installed PCE educational modules or detail view for
        specific PCE educational module.

        Kwargs:
            id: Id for the specific resource requested. If none, will return
                list of all members in resource class.
            **kwargs (dict): Key/value request query params.
        """
        self.logger.debug('Modules.GET() called')
        self.logger.debug('id: %s' % id)

        path = os.path.dirname(os.path.abspath(__file__)) + '/../../modules'
        if not os.path.isdir(path):
            # FIXME: Should return HTTP status 500.
            msg = 'Modules root folder does not exist'
            self.logger.error(msg)
            return self.JSON_response(status_code=-1, status_msg=msg)

        if id is None:
            modules = {
                name: self._build_module(name)
                for name in os.listdir(path)
            }
            self.logger.debug('Returning list of modules')
            return self.JSON_response(modules=modules)

        if not os.path.isdir(os.path.join(path, id)):
            # FIXME: Should return HTTP status 404.
            msg = 'Module %s does not exist' % id
            self.logger.warn(msg)
            return self.JSON_response(status_code=-2, status_msg=msg, url=False)

        self.logger.debug('Returning module %s' % id) 
        return self.JSON_response(id=id, module=self._build_module(id))

    def _build_module(self, module):
        """Return dict rep of PCE educational module.

        Args:
            module: Identifier of the module.
        """
        return {
            'url': self._build_url(id=module)
        }

    def _build_url(self, id=None):
        """Return URL for given module, or module base.
        
        Kwargs:
            module (str): Name of module to provide URL for. If 'None', returns
                base URL for modules resource. DEFAULT: None.
        """
        if id:
            return self.url_base + id + '/'
        return self.url_base
