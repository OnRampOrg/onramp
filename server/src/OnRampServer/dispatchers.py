"""Dispatchers implementing the OnRamp Server API.

Exports:
    Root: Root directoy
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
from configobj import ConfigObj
from Crypto import Random
from Crypto.Cipher import AES
from validate import Validator

class _ServerResourceBase:
    """Provide functionality needed by all OnRamp Server resource dispatchers.

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
        """Instantiate OnRamp Server Resource.

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


########################################################
 
class Root(_ServerResourceBase):

    def GET(self, id=None, **kwargs):
        self.logger.debug('Root.GET() called')
        self.logger.debug('id: %s' % id)
        #host = cherrypy.request.headers('Host')
        host = cherrypy.request.headers.get('Host', None)
        return "OnRamp Server is running... (%s)" % host

