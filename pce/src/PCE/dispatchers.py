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

import cherrypy

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


class Modules(_OnRampDispatcher):
    def GET(self, id=None, *args, **kwargs):
        self.log_call('GET')
        if args:
            cherrypy.response.status = 404
            return self.get_response(status_code=-404,
                                     status_msg='Resource does not exist')
        return self.get_response()

    def POST(self, id=None, mod_id=None, mod_name=None, location=None,
             **kwargs):

        self.log_call('POST')
        if id:
            # Module already installed, check params and deploy.
            pass
        else:
            # Module not yet installed, check params and install.
            pass

        return self.get_response()

    def PUT(self, id, mod_id, mod_name):
        self.log_call('PUT')
        return self.get_response()

    def DELETE(self, id):
        self.log_call('DELETE')
        return self.get_response()


class Jobs(_OnRampDispatcher):
    def GET(self, id):
        self.log_call('GET')
        return self.get_response()

    def POST(self, id=None):
        self.log_call('POST')
        if id:
            cherrypy.response.status = 400
        return self.get_response()

    def PUT(self, id):
        self.log_call('PUT')
        return self.get_response()

    def DELETE(self, id):
        self.log_call('DELETE')
        return self.get_response()


class Cluster(_OnRampDispatcher):
    def GET(self):
        self.log_call('GET')
        return self.get_response()
