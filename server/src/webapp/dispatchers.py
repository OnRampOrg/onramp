"""Dispatchers implementing the OnRamp Server API.

Exports:
    Root: Root directoy
"""

#
# https://cherrypy.readthedocs.org/en/3.3.0/tutorial/REST.html
#

import pprint
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

import webapp.onramppce as onramppce
import webapp.onrampdb as onrampdb

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
        ...
    """

    exposed = True

    def __init__(self, conf):
        """Instantiate OnRamp Server Resource.

        Args:
            conf (ConfigObj): Application configuration object.
        """
        self.conf = conf
        self.logger = logging.getLogger('onramp')

        server = None
        if 'url_docroot' in conf['server'].keys():
            server = conf['server']['url_docroot']
        else:
            server = conf['server']['socket_host'] + ':' + str(conf['server']['socket_port'])

        self.url_base = (server + '/' + self.__class__.__name__.lower() + '/')
        self.api_root = (server + '/api/')

        # Define the Database - SQLite
        self.logger.debug("Connecting to the database")
        rtn = onrampdb.define_database(self.logger, 'sqlite', {'filename' : os.getcwd() + '/../tmp/onramp_sqlite.db'} )
        if rtn != 0:
            sys.exit(-1)

    def _get_is_valid_fns(self):
        return {'user' :      onrampdb.is_valid_user_id,
                'workspace' : onrampdb.is_valid_workspace_id,
                'pce' :       onrampdb.is_valid_pce_id,
                'module' :    onrampdb.is_valid_module_id,
                'job' :       onrampdb.is_valid_job_id
                }

    def _check_auth(self, prefix, auth):
        if onrampdb.check_user_auth( auth ) is False:
            self.logger.debug(prefix + " Authorization Failed: 'auth' key invalid")
            raise cherrypy.HTTPError(401)
        return True

    def _update_session(self, auth):
        return True

########################################################
 

########################################################
# Root
########################################################
class Root(_ServerResourceBase):

    #
    # GET / : Server status
    #
    def GET(self, **kwargs):
        self.logger.debug('Root.GET()')
        return "OnRamp Server is running...\n"


########################################################
# Users
########################################################
class Users(_ServerResourceBase):

    # GET /users
    #     /users/:ID
    #     /users/:ID/workspaces
    #     /users/:ID/jobs
    #     /users/:ID/jobs?workspace=ID&pce=ID&module=ID
    @cherrypy.popargs('level')
    def GET(self, user_id=None, level=None, **kwargs):
        self.logger.debug('Users.GET()')

        allowed_levels = ["workspaces", "jobs"]
        allowed_search = ["workspace", "pce", "module"]
        valid_fns = self._get_is_valid_fns()

        debug = "All"
        ids = {}

        #
        # Parse the arguments
        #
        if user_id is not None:
            if valid_fns['user'](user_id) is False:
                raise cherrypy.HTTPError(400)
            debug = "Specific User " + user_id

        if level is not None:
            if level not in allowed_levels:
                raise cherrypy.NotFound()
            debug += " at " + level

        for key, value in kwargs.iteritems():
            if key not in allowed_search:
                raise cherrypy.HTTPError(400)
            if valid_fns[key](value) is False:
                raise cherrypy.HTTPError(400)

            ids[key] = value
            debug += "("+key+"="+value+")"


        self.logger.debug('Users.GET(): %s' % debug)

        #
        # Perform the correct operation
        #

        return "Users: %s\n" % debug

    #
    # POST /users/:ID
    #
    def POST(self, id=None, **kwargs):
        self.logger.debug('Users.POST()')

        allowed_search = ["name", "email"]

        for key, value in kwargs.iteritems():
            if key not in allowed_search:
                raise cherrypy.HTTPError(400)
            self.logger.debug("Users.POST(): %s=%s" % (key, value) )

        return "Users: \n"


########################################################
# Workspaces
########################################################
class Workspaces(_ServerResourceBase):

    # GET /workspaces
    #     /workspaces/:ID
    #     /workspaces/:ID/doc
    #     /workspaces/:ID/users
    #     /workspaces/:ID/pcemodulepairs
    #     /workspaces/:ID/jobs
    #     /workspaces/:ID/jobs?user=ID&pce=ID&module=ID
    @cherrypy.popargs('level')
    def GET(self, workspace_id=None, level=None, **kwargs):
        self.logger.debug('Workspaces.GET()')

        allowed_levels = ["doc", "users", "pcemodulepairs", "jobs"]
        allowed_search = ["user", "pce", "module"]
        valid_fns = self._get_is_valid_fns()

        debug = "All"
        ids = {}

        #
        # Parse the arguments
        #
        if workspace_id is not None:
            if valid_fns['workspace'](workspace_id) is False:
                raise cherrypy.HTTPError(400)
            debug = "Specific Workspace " + workspace_id

        if level is not None:
            if level not in allowed_levels:
                raise cherrypy.NotFound()
            debug += " at " + level

        for key, value in kwargs.iteritems():
            if key not in allowed_search:
                raise cherrypy.HTTPError(400)
            if valid_fns[key](value) is False:
                raise cherrypy.HTTPError(400)

            ids[key] = value
            debug += "("+key+"="+value+")"


        self.logger.debug('Workspaces.GET(): %s' % debug)

        #
        # Perform the correct operation
        #

        return "Workspace: %s\n" % debug


########################################################
# PCEs
########################################################
class PCEs(_ServerResourceBase):

    # GET /pces
    #     /pces/:ID
    #     /pces/:ID/doc
    #     /pces/:ID/workspaces
    #     /pces/:ID/modules
    #     /pces/:ID/jobs
    #     /pces/:ID/jobs?user=ID&workspace=ID&module=ID
    @cherrypy.popargs('level')
    def GET(self, pce_id=None, level=None, **kwargs):
        self.logger.debug('PCEs.GET()')

        allowed_levels = ["doc", "workspaces", "modules", "jobs"]
        allowed_search = ["user", "workspace", "module"]
        valid_fns = self._get_is_valid_fns()

        debug = "All"
        ids = {}

        #
        # Parse the arguments
        #
        if pce_id is not None:
            if valid_fns['pce'](pce_id) is False:
                raise cherrypy.HTTPError(400)
            debug = "Specific PCE " + pce_id

        if level is not None:
            if level not in allowed_levels:
                raise cherrypy.NotFound()
            debug += " at " + level

        for key, value in kwargs.iteritems():
            if key not in allowed_search:
                raise cherrypy.HTTPError(400)
            if valid_fns[key](value) is False:
                raise cherrypy.HTTPError(400)

            ids[key] = value
            debug += "("+key+"="+value+")"


        self.logger.debug('PCEs.GET(): %s' % debug)

        #
        # Perform the correct operation
        #

        return "PCE: %s\n" % debug


########################################################
# Modules
########################################################
class Modules(_ServerResourceBase):

    # GET /modules
    #     /modules/:ID
    #     /modules/:ID/doc
    #     /modules/:ID/pces
    #     /modules/:ID/jobs
    #     /modules/:ID/jobs?user=ID&workspace=ID&pce=ID
    @cherrypy.popargs('level')
    def GET(self, module_id=None, level=None, **kwargs):
        self.logger.debug('Modules.GET()')

        allowed_levels = ["doc", "pces", "jobs"]
        allowed_search = ["user", "workspace", "pce"]
        valid_fns = self._get_is_valid_fns()

        debug = "All"
        ids = {}

        #
        # Parse the arguments
        #
        if module_id is not None:
            if valid_fns['module'](module_id) is False:
                raise cherrypy.HTTPError(400)
            debug = "Specific Module " + module_id

        if level is not None:
            if level not in allowed_levels:
                raise cherrypy.NotFound()
            debug += " at " + level

        for key, value in kwargs.iteritems():
            if key not in allowed_search:
                raise cherrypy.HTTPError(400)
            if valid_fns[key](value) is False:
                raise cherrypy.HTTPError(400)

            ids[key] = value
            debug += "("+key+"="+value+")"


        self.logger.debug('Modules.GET(): %s' % debug)

        #
        # Perform the correct operation
        #

        return "Module: %s\n" % debug

########################################################
# Jobs
########################################################
class Jobs(_ServerResourceBase):

    # GET /jobs
    #     /jobs/:ID
    #     /jobs/:ID/data
    @cherrypy.popargs('level')
    def GET(self, job_id=None, level=None, **kwargs):
        self.logger.debug('Jobs.GET()')

        allowed_levels = ["data"]
        allowed_search = []
        valid_fns = self._get_is_valid_fns()

        debug = "All"
        ids = {}

        #
        # Parse the arguments
        #
        if job_id is not None:
            if valid_fns['job'](job_id) is False:
                raise cherrypy.HTTPError(400)
            debug = "Specific Job " + job_id

        if level is not None:
            if level not in allowed_levels:
                raise cherrypy.NotFound()
            debug += " at " + level

        for key, value in kwargs.iteritems():
            if key not in allowed_search:
                raise cherrypy.HTTPError(400)
            if valid_fns[key](value) is False:
                raise cherrypy.HTTPError(400)

            ids[key] = value
            debug += "("+key+"="+value+")"


        self.logger.debug('Jobs.GET(): %s' % debug)

        #
        # Perform the correct operation
        #

        return "Job: %s\n" % debug

    #
    # POST /jobs
    #
    def POST(self, id=None, **kwargs):
        self.logger.debug('Jobs.POST()')

        allowed_search = ["foo", "bar"]

        for key, value in kwargs.iteritems():
            if key not in allowed_search:
                raise cherrypy.HTTPError(400)
            self.logger.debug("Jobs.POST(): %s=%s" % (key, value) )

        return "Jobs: \n"

    #
    # DELETE /jobs/:ID
    #
    def DELETE(self, id=None, **kwargs):
        self.logger.debug('Jobs.DELETE()')

        if id is None:
            raise cherrypy.HTTPError(400)

        return "Jobs: "+id+"\n"

########################################################
# Login
########################################################
class Login(_ServerResourceBase):

    # POST /login
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self, id=None, **kwargs):
        prefix = '[POST /login]'
        self.logger.debug(prefix)

        rtn = {}
        rtn['status'] = 0
        rtn['status_message'] = 'Success'

        if not hasattr(cherrypy.request, "json"):
            self.logger.error(prefix + " No json data sent")
            raise cherrypy.HTTPError(400)

        data = cherrypy.request.json

        #
        # Make sure the required fields have been specified
        #
        allowed_search = ["username", "password"]
        for key in allowed_search:
            if key not in data:
                self.logger.error(prefix + " Missing key \"" + key + "\"")
                raise cherrypy.HTTPError(400, "Bad Request ...")

        #
        # Ask the database if this is a valid user
        #
        self.logger.info(prefix + " Attempt \"" + data["username"] + "\"")

        user_auth = onrampdb.user_login( data["username"], data["password"])
        
        if user_auth is not None:
            rtn['auth'] = user_auth
            rtn['auth']['username'] = data["username"]
            self.logger.info(prefix + " Attempt \"" + data["username"] + "\" Success")
        else:
            self.logger.info(prefix + " Attempt \"" + data["username"] + "\" Failed")
            raise cherrypy.HTTPError(401)

        #
        # Tell the user
        #

        return rtn

    # DELETE /login --> Logout
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def DELETE(self, id=None, **kwargs):
        prefix = '[DELETE /login]'
        self.logger.debug(prefix)

        rtn = {}
        rtn['status'] = 0
        rtn['status_message'] = 'Success'

        if not hasattr(cherrypy.request, "json"):
            self.logger.error(prefix + " No json data sent")
            raise cherrypy.HTTPError(400)

        data = cherrypy.request.json

        #
        # Make sure the required fields have been specified
        #

        #
        # Ask the database if this is a valid user
        #

        #
        # Tell the user
        #

        return rtn

########################################################
# Admin
########################################################
class Admin(_ServerResourceBase):

    # GET
    #      /admin/pce/:PCEID
    #      /admin/pce/:PCEID/module/:MODULEID
    @cherrypy.popargs('level', 'pce_id', 'mlevel', 'module_id')
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def GET(self, level, pce_id, mlevel=None, module_id=None, **kwargs):
        prefix = "[GET /admin/"+level+"/"+str(pce_id)+"]"
        self.logger.debug(prefix)

        rtn = {}
        rtn['status'] = 0
        rtn['status_message'] = 'Success'

        debug = "Any"

        #
        # Allowed levels and dispatch
        #
        if mlevel is not None:
            if mlevel != "module" or module_id is None:
                self.logger.error(prefix + " Invalid level or ID")
                raise cherrypy.NotFound()
            else:
                prefix = prefix[:-1] + "/module/"+str(module_id)+"]"
                rdata = self._process_module_get(pce_id, module_id)
                rtn['module'] = rdata
        elif level != "pce":
            self.logger.error(prefix + " Invalid level")
            raise cherrypy.NotFound()
        else:
            rdata = self._process_pce_get(pce_id)
            rtn['pce'] = rdata

        self.logger.debug(prefix + ' Done')

        return rtn

    ############################################################
    # Module Get
    ############################################################
    def _process_module_get(self, pce_id, module_id):
        return {}

    ############################################################
    # PCE Get
    ############################################################
    def _process_pce_get(self, pce_id):
        return {}


    # POST / DELETE / PUT
    #      /admin/user
    #      /admin/module
    #      /admin/workspace
    #      /admin/workspace/:WORKSPACEID/user/:USERID
    #      /admin/workspace/:WORKSPACEID/pcemodulepairs/:PCEID/:MODULEID
    #      /admin/pce
    #      /admin/pce/:PCEID/module/:MODULEID
    @cherrypy.popargs('level1', 'level1_id', 'level2', 'level2_id', 'level3_id')
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self, level1=None, level1_id=None, level2=None, level2_id=None, level3_id=None, **kwargs):
        prefix = '[POST /admin/]'
        self.logger.debug(prefix)

        rtn = {}
        rtn['status'] = 0
        rtn['status_message'] = 'Success'

        allowed_level1 = {'user' :      self._process_user,
                          'module' :    self._process_module,
                          'workspace' : self._process_workspace,
                          'pce' :       self._process_pce,
                          }
        debug = "Any"

        #
        # Level 1 is required
        #
        if level1 is None:
            raise cherrypy.NotFound()
        elif level1 not in allowed_level1.keys():
            raise cherrypy.HTTPError(400)

        if not hasattr(cherrypy.request, "json"):
            self.logger.error(prefix + " No json data sent")
            raise cherrypy.HTTPError(400)

        data = cherrypy.request.json

        #
        # Check auth
        # TODO needs improvement
        #
        self.logger.debug(prefix + " Checking authorization")
        if 'auth' not in data.keys():
            self.logger.debug(prefix + " Authorization Failed: No 'auth' key")
            raise cherrypy.HTTPError(401)
        elif self._check_auth(prefix, data['auth']) is True:
            self.logger.debug(prefix + " Authorization Success")

        #
        # Dispatch to the correct handler
        #
        debug = level1

        if level1 == "user" or level1 == "module":
            rdata = allowed_level1[level1]("POST", data, level1_id, kwargs)
        else:
            rdata = allowed_level1[level1]("POST", data, level1_id, level2, level2_id, level3_id, kwargs)

        rtn[level1] = rdata

        return rtn

    ########################################################
    # User
    ########################################################
    def _process_user(self, type, data, user_id=None, kwargs=None):
        prefix = '['+type+' /admin/user]'
        rdata = {}

        #
        # Adding a new user
        # /admin/user
        #
        if user_id is None:
            self.logger.info(prefix + " Adding \"" + data["username"] + "\"")
            rdata = onrampdb.user_add_if_new( data["username"], data["password"] )
            user_id = rdata['id']
        #
        # Note implemented
        #
        else:
            raise cherrypy.NotFound()

        self.logger.debug(prefix + ' process_user(%s, %s)' % (type, user_id))

        return rdata


    ########################################################
    # Workspace
    ########################################################
    def _process_workspace(self, type, data, workspace_id=None, 
                          level2=None, level2_id=None, level3_id=None, kwargs=None):
        prefix = '['+type+' /admin/workspace]'
        rdata = {}

        #
        # Adding a new workspace
        # /admin/workspace
        #
        if workspace_id is None:
            self.logger.info(prefix + " Adding \"" + data["name"] + "\"")
            rdata = onrampdb.workspace_add_if_new( data["name"] )
            workspace_id = rdata['id']
        #
        # Associate a user with a workspace
        # /admin/workspace/:WID/user/:USERID
        #
        elif level2 is not None and level2_id is not None and level3_id is None and level2 == "user":
            user_id = level2_id
            prefix = prefix[:-1] + "/" + str(workspace_id) + "/user/" + str(user_id) + "]"
            self.logger.info(prefix + " Associate user " + str(user_id) + " with workspace "+str(workspace_id))

            # Add the result
            rdata = onrampdb.workspace_add_user( workspace_id, user_id )
            if 'error_msg' in rdata.keys():
                self.logger.info(prefix + " " + rdata['error_msg'])
                raise cherrypy.HTTPError(400)
        #
        # Associate a PCE/Module pair with a workspace
        # /admin/workspace/:WID/pcemodulepairs/:PCEID/:MODULEID
        #
        elif level2 is not None and level2 == "pcemodulepairs" and level2_id is not None and level3_id is not None:
            pce_id = level2_id
            module_id = level3_id
            prefix = prefix[:-1] + "/" + str(workspace_id) + "/pcemodulepairs/" + str(pce_id) + "/" + str(module_id)+"]"
            self.logger.info(prefix + " Associate PCE/Module pair (" + str(pce_id) + ", " + str(module_id) + " with workspace "+str(workspace_id))

            # Add the result
            rdata = onrampdb.workspace_add_pair( workspace_id, pce_id, module_id )
            if 'error_msg' in rdata.keys():
                self.logger.info(prefix + " " + rdata['error_msg'])
                raise cherrypy.HTTPError(400)

        #
        # Other not handled
        #
        else:
            self.logger.error(prefix + " Missing one or more arguments (" + level2 + ","+ str(level2_id)+","+str(level3_id) +")")
            raise cherrypy.NotFound()

        self.logger.debug(prefix + ' process_workspace(%s, %s)' % (type, workspace_id))

        return rdata


    ########################################################
    # PCE
    ########################################################
    def _process_pce(self, type, data, pce_id=None,
                    level2=None, level2_id=None, level3_id=None, kwargs=None):
        prefix = '['+type+' /admin/pce]'
        rdata = {}

        #
        # Adding a new PCE
        # /admin/pce
        #
        if pce_id is None:
            self.logger.info(prefix + " Adding \"" + data["name"] + "\"")
            rdata = onrampdb.pce_add_if_new( data["name"] )
            pce_id = rdata['id']
        #
        # Associate a module with a PCE
        # /admin/pce/:PCEID/module/:MODULEID
        #
        elif level2 is not None and level2 == "module" and level2_id is not None and level3_id is None:
            module_id = level2_id
            prefix = prefix[:-1] + "/" + str(pce_id) + "/module/" + str(module_id) + "]"
            self.logger.info(prefix + " Associate module " + str(module_id) + " with PCE "+str(pce_id))

            # Add the result
            rdata = onrampdb.pce_add_module( pce_id, module_id )
            if 'error_msg' in rdata.keys():
                self.logger.info(prefix + " " + rdata['error_msg'])
                raise cherrypy.HTTPError(400)
        #
        # Other not handled
        #
        else:
            self.logger.error(prefix + " Missing one or more arguments (" + 
                              level2 + ","+ str(level2_id)+","+str(level3_id) +")")
            raise cherrypy.NotFound()


        self.logger.debug(prefix + ' process_pce(%s, %s)' % (type, pce_id))

        return rdata


    ########################################################
    # Module
    ########################################################
    def _process_module(self, type, data, module_id=None, kwargs=None):
        prefix = '['+type+' /admin/module]'
        rdata = {}

        #
        # Adding a new module
        #
        if module_id is None:
            self.logger.info(prefix + " Adding \"" + data["name"] + "\"")
            rdata = onrampdb.module_add_if_new( data["name"] )
            module_id = rdata['id']
        #
        # Note implemented
        #
        else:
            raise cherrypy.NotFound()

        self.logger.debug(prefix + ' process_module(%s, %s)' % (type, module_id))

        return rdata

