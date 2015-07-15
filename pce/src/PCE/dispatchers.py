"""Dispatchers implementing the OnRamp PCE API.

Exports:
    Modules: View, add, update, and remove PCE educational modules.
    Jobs: Launch, update, remove, and get status of PCE jobs.
    validation_required: Validate rx'd user input to PCE dispatchers.
    auth_required: Verify user credentials prior to executing method decorated
        by this function.
    admin_auth_required: Verify admin credentials prior to executing method
        decorated by this function.
"""

import logging
import os

import cherrypy
from configobj import ConfigObj
from validate import Validator

class _OnRampDispatcher:
    exposed = True
    _cp_config = {
        'tools.json_out.on': True,
        'tools.json_in.on': True
    }

    def __init__(self, conf, log_name):
        self.conf = conf
        self.logger = logging.getLogger(log_name)
        self.logger.debug('Initialized %s' % self.__class__.__name__)

    def get_response(self, status_code=0, status_msg='Success', **kwargs):
        response = {
            'status_code': status_code,
            'status_msg': status_msg
        }
        response.update(kwargs)
        return response

    def log_call(self, func_name):
        self.logger.debug('%s.%s() called' % (self.__class__.__name__,
                                                func_name))

    def validate_json(self, data, func_name):
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
    def GET(self, id=None, **kwargs):
        self.log_call('GET')

        # Return the resource.
        return self.get_response()

    def POST(self, id=None, **kwargs):
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
        self.log_call('PUT')

        # Overwrite the resource.
        return self.get_response()

    def DELETE(self, id, **kwargs):
        self.log_call('DELETE')

        # Delete the resource.
        return self.get_response()


class Jobs(_OnRampDispatcher):
    def GET(self, id, **kwargs):
        self.log_call('GET')

        # Return the resource.
        return self.get_response()

    def POST(self, **kwargs):
        self.log_call('POST')
        data = cherrypy.request.json
        result = self.validate_json(data, 'POST')
        if result:
            return result
        
        # Launch job.
        return self.get_response()

    def PUT(self, id, **kwargs):
        self.log_call('PUT')
        return self.get_response()

    def DELETE(self, id, **kwargs):
        self.log_call('DELETE')
        return self.get_response()


class Cluster(_OnRampDispatcher):
    def GET(self, **kwargs):
        self.log_call('GET')
        return self.get_response()
