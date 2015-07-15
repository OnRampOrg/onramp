"""Dispatchers implementing the OnRamp PCE API.

Exports:
    Modules: View, add, update, and remove PCE educational modules.
    Jobs: Launch, update, remove, and get status of PCE jobs.
    Cluster: View cluster status.
"""

import logging
import os

import cherrypy
from configobj import ConfigObj
from validate import Validator

class _OnRampDispatcher:
    """Base class for OnRamp PCE dispatchers."""
    exposed = True
    _cp_config = {
        'tools.json_out.on': True,
        'tools.json_in.on': True
    }

    def __init__(self, conf, log_name):
        """Initialize an OnRamp PCE dispatcher.

        Args:
            conf (ConfigObj): Application/server configuration object.
            log_name (str): Name of an initialized logger to use.
        """
        self.conf = conf
        self.logger = logging.getLogger(log_name)
        self.logger.debug('Initialized %s' % self.__class__.__name__)

    def get_response(self, status_code=0, status_msg='Success', **kwargs):
        """Build and return and OnRamp PCE dispatcher response dict.

        Kwargs:
            status_code (int): Error/success indication.
            status_msg (str): Detailed information about response result.
            **kwargs (dict): Additional key/val pairs to include in the
                response.
        """
        response = {
            'status_code': status_code,
            'status_msg': status_msg
        }
        response.update(kwargs)
        return response

    def log_call(self, func_name):
        """Log entry into the given dispatcher.
        
        Args:
            func_name (str): The name of the function handling the request.
        """
        self.logger.debug('%s.%s() called' % (self.__class__.__name__,
                                                func_name))

    def validate_json(self, data, func_name):
        """Validate contents of JSON request body.

        Loads configspec file by classname and func_name.

        Args:
            data (dict): The JSON request body to validate.
            func_name (str): The name of the function requiring validation.
        """
        def _search_dict(d, prefix=''):
            bad_params = []
            for item in d.keys():
                if isinstance(d[item], dict):
                    bad = _search_dict(d[item], '%s[%s]' % (prefix, item))
                    bad_params += bad
                else:
                    if not d[item]:
                        bad_params.append('%s%s' % (prefix, item))
            return bad_params
            
        self.logger.debug('Validating input to %s.%s()'
                          % (self.__class__.__name__, func_name))
    
        path = os.path.dirname(os.path.abspath(__file__)) + '/../..'
        configspec = (path + '/src/configspecs/%s_%s.inputspec'
                      % (self.__class__.__name__, func_name))
    
        try:
            conf = ConfigObj(data, configspec=configspec)
            result = conf.validate(Validator(), preserve_errors=True)
            self.logger.debug('Result: %s' % str(result))
        except IOError as ie:
            self.logger.error(str(ie))
            cherrypy.response.status = 500
            return self.get_response(status_code=-9, status_msg=str(ie))
        except ValueError as ve:
            self.logger.warn(str(ve))
            cherrypy.response.status = 400
            return self.get_response(status_code=-8, status_msg=str(ve))

        if isinstance(result, dict):
            invalid_params = _search_dict(result)
            msg = ('An invalid value or no value was received for the '
                   'following required parameter(s): %s'
                   % ', '.join(invalid_params))
            self.logger.warn(msg)
            cherrypy.response.status = 400
            return self.get_response(status_code=-8, status_msg=msg)
    
        return None


class Modules(_OnRampDispatcher):
    """Provide API for OnRamp educational modules resource.

    Methods:
        GET: Return list of installed modules or detail view for specific
            module.
        POST: Clone/copy a new module or deploy a previously cloned/copied
            module.
        PUT: Update a specific module.
        DELETE: Remove a specific module.
    """
    def GET(self, id=None, **kwargs):
        """Return list of installed modules or detail view for specific module.

        Kwargs:
            id (str): None signals list get, if not None, return specific
                module.
            **kwargs (dict): HTTP query-string parameters. Not currently used.
        """
        self.log_call('GET')

        # Return the resource.
        return self.get_response()

    def POST(self, id=None, **kwargs):
        """Clone/copy a new module or deploy a previously cloned/copied module.

        Kwargs:
            id (str): None signals clone/copy of new module. If not None, deploy
                module corresponding to id.
            **kwargs (dict): HTTP query-string parameters. Not currently used.
        """
        self.log_call('POST')

        if id:
            # Module already installed, verify id and deploy.
            pass
        else:
            # Module not yet installed, check params and install.
            data = cherrypy.request.json
            result = self.validate_json(data, 'POST')
            if result:
                return result

        return self.get_response()

    def PUT(self, id, **kwargs):
        """Update a specific module.

        Args:
            id (str): Id of the module to update.

        Kwargs:
            **kwargs (dict): HTTP query-string parameters. Not currently used.
        """
        self.log_call('PUT')

        # Overwrite the resource.
        return self.get_response()

    def DELETE(self, id, **kwargs):
        """Delete a specific module.

        Args:
            id (str): Id of the module to delete.

        Kwargs:
            **kwargs (dict): HTTP query-string parameters. Not currently used.
        """
        self.log_call('DELETE')

        # Delete the resource.
        return self.get_response()


class Jobs(_OnRampDispatcher):
    """Provide API for OnRamp jobs resource.

    Methods:
        GET: Get status/results for specific job.
        POST: Launch a new job.
        PUT: Update a specific job.
        DELETE: Delete a specific job.
    """
    def GET(self, id, **kwargs):
        """Get status/results for specific job.

        Args:
            id (str): Id of the job to inspect.

        Kwargs:
            **kwargs (dict): HTTP query-string parameters. Not currently used.
        """
        self.log_call('GET')

        # Return the resource.
        return self.get_response()

    def POST(self, **kwargs):
        """Launch a new job.

        Kwargs:
            **kwargs (dict): HTTP query-string parameters. Not currently used.
        """
        self.log_call('POST')
        data = cherrypy.request.json
        result = self.validate_json(data, 'POST')
        if result:
            return result
        
        # Launch job.
        return self.get_response()

    def PUT(self, id, **kwargs):
        """Update a specific job.

        Args:
            id (str): Id of the job to update.

        Kwargs:
            **kwargs (dict): HTTP query-string parameters. Not currently used.
        """
        self.log_call('PUT')

        # Overwrite the resource.
        return self.get_response()

    def DELETE(self, id, **kwargs):
        """Delete a specific job.

        Args:
            id (str): Id of the job to delete.

        Kwargs:
            **kwargs (dict): HTTP query-string parameters. Not currently used.
        """
        self.log_call('DELETE')

        # Delete the resource.
        return self.get_response()


class Cluster(_OnRampDispatcher):
    """Provide API for OnRamp cluster.

    Methods:
        GET: Return cluster status/info.
    """
    def GET(self, **kwargs):
        """Return cluster status/info.

        Kwargs:
            **kwargs (dict): HTTP query-string parameters. Not currently used.
        """
        self.log_call('GET')

        # Return the resource.
        return self.get_response()
