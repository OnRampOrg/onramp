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

    _db = None
    _tmp_dir = ""

    def __init__(self, conf):
        """Instantiate OnRamp Server Resource.

        Args:
            conf (ConfigObj): Application configuration object.
        """
        self.conf = conf
        self.logger = logging.getLogger('onramp')

        self._tmp_dir = conf['tmp_dir']

        server = None
        if 'url_docroot' in conf['server'].keys():
            server = conf['server']['url_docroot']
        else:
            server = conf['server']['socket_host'] + ':' + str(conf['server']['socket_port'])

        self.url_base = (server + '/' + self.__class__.__name__.lower() + '/')
        self.api_root = (server + '/api/')

        # Define the Database - SQLite
        self.logger.debug("Setup database credentials")
        self._db = onrampdb.DBAccess(self.logger, 'sqlite', {'filename' : os.getcwd() + '/../tmp/onramp_sqlite.db'} )
        if self._db is None:
            self.logger.error("No DB connection present")
            sys.exit(-1)

        # Setup an object for the PCE connections
        self._pces = {}
        self.logger.debug("Checking PCE Connections")
        all_pce_ids = self._db.pce_get_all_ids()
        if len(all_pce_ids) <= 0:
            self.logger.info("No PCE Connections Available")
        for pce_id in all_pce_ids:
            self._pces[pce_id] = onramppce.PCEAccess(self.logger, self._db, pce_id, self._tmp_dir)

    def _get_is_valid_fns(self):
        return {'user' :      self._db.is_valid_user_id,
                'workspace' : self._db.is_valid_workspace_id,
                'pce' :       self._db.is_valid_pce_id,
                'module' :    self._db.is_valid_module_id,
                'job' :       self._db.is_valid_job_id
                }

    def _check_user_apikey(self, prefix, apikey):
        if self._db.check_user_apikey( apikey ) is False:
            return False
        return True

    def _check_auth(self, prefix, auth, req_admin=False, throw_error=True):
        if self._db.check_user_auth( auth, req_admin ) is False:
            if throw_error is True:
                self.logger.debug(prefix + " Authorization Failed: 'auth' key invalid")
                raise cherrypy.HTTPError(401)
            return False
        else:
            self._db.user_update( auth );

        return True

    def _not_implemented(self, prefix):
        self.logger.debug(prefix + " Not implemented")
        rtn = {}
        rtn['status'] = -1
        rtn['status_message'] = prefix + " Please implement this method..."
        return rtn

    def _return_error(self, prefix, code, msg):
        self.logger.debug(prefix + " Error ("+str(code)+") = " + msg)
        rtn = {}
        rtn['status'] = code
        rtn['status_message'] = msg
        return rtn

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
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def GET(self, user_id=None, level=None, **kwargs):
        prefix = '[GET /users]'
        self.logger.debug(prefix)

        rtn = {}
        rtn['status'] = 0
        rtn['status_message'] = 'Success'


        valid_fns = self._get_is_valid_fns()

        debug = "All"

        #
        # Make sure the required fields have been specified
        #
        self.logger.debug(prefix + " Checking authorization")
        if 'apikey' not in kwargs.keys():
            self.logger.debug(prefix + " Authorization Failed: No 'apikey' specified")
            raise cherrypy.HTTPError(401)
        elif self._check_user_apikey(prefix, kwargs['apikey']) is False:
            self.logger.debug(prefix + " Authorization Failed: Invalid 'apikey' specified")
            raise cherrypy.HTTPError(401)
        self.logger.debug(prefix + " Authorization Success")

        #
        # Find correct functionality
        #
        if user_id is not None:
            if valid_fns['user'](user_id) is False:
                raise cherrypy.HTTPError(400)

        #
        # /users/  : Get all users
        #
        if user_id is None:
            self.logger.debug(prefix + " Processing...")

            user_info = self._db.user_get_info()
            if user_info is None:
                self.logger.error(prefix + " Error no data found")
            else:
                self.logger.debug(prefix + " Package info for " + str(len(user_info['data'])) + " users")
                rtn['users'] = user_info

        #
        # /users/:ID  : Get profile for this user
        #
        elif level is None:
            prefix = prefix[:-1] + "/"+str(user_id)+"]"
            self.logger.debug(prefix + " Processing...")

            user_info = self._db.user_get_info(user_id)
            if user_info is None:
                self.logger.error(prefix + " Error no data found")
            else:
                self.logger.debug(prefix + " Package info for " + str(len(user_info)-1) + " user")
                rtn['users'] = user_info

        #
        # /users/:ID/workspace
        #
        elif level is not None and level == "workspaces":
            prefix = prefix[:-1] + "/"+str(user_id)+"/"+level+"]"
            self.logger.debug(prefix + " Processing...")

            user_info = self._db.user_get_workspaces(user_id)
            if user_info is None:
                self.logger.error(prefix + " Error no data found")
            else:
                self.logger.debug(prefix + " Package info contains " + str(len(user_info['data'])) + " workspaces")
                rtn['users'] = user_info

        #
        # /users/:ID/jobs
        #
        elif level is not None and level == "jobs":
            prefix = prefix[:-1] + "/"+str(user_id)+"/"+level+"]"
            self.logger.debug(prefix + " Processing...")

            #
            # Process keys
            #
            allowed_search = ["apikey", "workspace", "pce", "module", "state"]

            ids = {}
            debug = ""
            for key, value in kwargs.iteritems():
                self.logger.debug(prefix + " Key/Value (" + key + ", " + str(value) + ")")
                if key not in allowed_search:
                    raise cherrypy.HTTPError(400)
                elif key == "state":
                    ids[key] = value
                    if type(value) is list:
                        debug += "("+key+"="+ (",".join(value)) +")"
                    else:
                        debug += "("+key+"="+value+")"
                elif key != "apikey":
                    ids[key+"_id"] = value
                    debug += "("+key+"="+value+")"

            self.logger.debug(prefix + " Processing... " + debug)
            user_info = self._db.user_get_jobs(user_id, ids)
            if user_info is None:
                self.logger.error(prefix + " Error no data found")
            else:
                self.logger.debug(prefix + " Package info contains " + str(len(user_info['data'])) + " jobs")
                rtn['users'] = user_info

        #
        # Unknown
        #
        else:
            raise cherrypy.HTTPError(400)

        #
        # Perform the correct operation
        #

        return rtn

    #
    # POST /users/:ID
    #
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self, id, **kwargs):
        prefix = '[POST /users/'+str(id)+']'
        self.logger.debug(prefix)

        rtn = {}
        rtn['status'] = 0
        rtn['status_message'] = 'Success'

        return self._not_implemented(prefix)

        #
        # Make sure the required fields have been specified
        #
        allowed_search = ["name", "email"]

        for key, value in kwargs.iteritems():
            if key not in allowed_search:
                raise cherrypy.HTTPError(400)
            self.logger.debug("Users.POST(): %s=%s" % (key, value) )

        return rtn


########################################################
# Workspaces
########################################################
class Workspaces(_ServerResourceBase):

    # GET /workspaces
    #     /workspaces/:ID
    #     /workspaces/:ID/docs
    #     /workspaces/:ID/users
    #     /workspaces/:ID/pcemodulepairs
    #     /workspaces/:ID/jobs
    #     /workspaces/:ID/jobs?user=ID&pce=ID&module=ID
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @cherrypy.popargs('level')
    def GET(self, workspace_id=None, level=None, **kwargs):
        prefix = '[GET /workspaces]'
        self.logger.debug(prefix)

        rtn = {}
        rtn['status'] = 0
        rtn['status_message'] = 'Success'


        valid_fns = self._get_is_valid_fns()


        #
        # Make sure the required fields have been specified
        #
        self.logger.debug(prefix + " Checking authorization")
        if 'apikey' not in kwargs.keys():
            self.logger.debug(prefix + " Authorization Failed: No 'apikey' specified")
            raise cherrypy.HTTPError(401)
        elif self._check_user_apikey(prefix, kwargs['apikey']) is False:
            self.logger.debug(prefix + " Authorization Failed: Invalid 'apikey' specified")
            raise cherrypy.HTTPError(401)
        self.logger.debug(prefix + " Authorization Success")


        #
        # Find correct functionality
        #
        if workspace_id is not None:
            if valid_fns['workspace'](workspace_id) is False:
                raise cherrypy.HTTPError(400)

        #
        # /workspaces
        #
        if workspace_id is None:
            self.logger.debug(prefix + " Processing...")

            workspace_info = self._db.workspace_get_info()
            if workspace_info is None:
                self.logger.error(prefix + " Error no data found")
            else:
                self.logger.debug(prefix + " Package info for " + str(len(workspace_info['data'])) + " workspaces")
                rtn['workspaces'] = workspace_info

        #
        # /workspaces/:ID
        #
        elif level is None:
            prefix = prefix[:-1] + "/"+str(workspace_id)+"]"
            self.logger.debug(prefix + " Processing...")

            workspace_info = self._db.workspace_get_info(workspace_id)
            if workspace_info is None:
                self.logger.error(prefix + " Error no data found")
            else:
                self.logger.debug(prefix + " Package info for " + str(len(workspace_info)-1) + " workspace")
                rtn['workspaces'] = workspace_info

        #
        # /workspaces/:ID/docs
        #
        elif level is not None and level == "docs":
            prefix = prefix[:-1] + "/"+str(workspace_id)+"/"+level+"]"
            self.logger.debug(prefix + " Processing...")

            workspace_info = self._db.workspace_get_doc(workspace_id)
            if workspace_info is None:
                self.logger.error(prefix + " Error no data found")
            else:
                self.logger.debug(prefix + " Package info for " + str(len(workspace_info)-1) + " workspace")
                rtn['workspaces'] = workspace_info

        #
        # /workspaces/:ID/users
        #
        elif level is not None and level == "users":
            prefix = prefix[:-1] + "/"+str(workspace_id)+"/"+level+"]"
            self.logger.debug(prefix + " Processing...")

            workspace_info = self._db.workspace_get_users(workspace_id)
            if workspace_info is None:
                self.logger.error(prefix + " Error no data found")
            else:
                self.logger.debug(prefix + " Package info for " + str(len(workspace_info)-1) + " workspace")
                rtn['workspaces'] = workspace_info
        #
        # /workspaces/:ID/pcemodulepairs
        #
        elif level is not None and level == "pcemodulepairs":
            prefix = prefix[:-1] + "/"+str(workspace_id)+"/"+level+"]"
            self.logger.debug(prefix + " Processing...")

            workspace_info = self._db.workspace_get_pairs(workspace_id)
            if workspace_info is None:
                self.logger.error(prefix + " Error no data found")
            else:
                self.logger.debug(prefix + " Package info for " + str(len(workspace_info)-1) + " workspace")
                rtn['workspaces'] = workspace_info

        #
        # /workspaces/:ID/jobs
        # /workspaces/:ID/jobs?user=ID&pce=ID&module=ID
        #
        elif level is not None and level == "jobs":
            prefix = prefix[:-1] + "/"+str(workspace_id)+"/"+level+"]"
            self.logger.debug(prefix + " Processing...")

            #
            # Process keys
            #
            allowed_search = ["apikey", "user", "pce", "module", "state"]
            ids = {}
            debug = ""
            for key, value in kwargs.iteritems():
                self.logger.debug(prefix + " Key/Value (" + key + ", " + str(value) + ")")
                if key not in allowed_search:
                    raise cherrypy.HTTPError(400)
                elif key == "state":
                    ids[key] = value
                    if type(value) is list:
                        debug += "("+key+"="+ (",".join(value)) +")"
                    else:
                        debug += "("+key+"="+value+")"
                elif key != "apikey":
                    ids[key+"_id"] = value
                    debug += "("+key+"="+value+")"

            self.logger.debug(prefix + " Processing... " + debug)
            workspace_info = self._db.workspace_get_jobs(workspace_id, ids)
            if workspace_info is None:
                self.logger.error(prefix + " Error no data found")
            else:
                self.logger.debug(prefix + " Package info contains " + str(len(workspace_info['data'])) + " jobs")
                rtn['workspaces'] = workspace_info

        #
        # Unknown
        #
        else:
            raise cherrypy.HTTPError(400)

        #
        # Perform the correct operation
        #

        return rtn


########################################################
# PCEs
########################################################
class PCEs(_ServerResourceBase):

    # GET /pces
    #     /pces/:ID
    #     /pces/:ID/docs
    #     /pces/:ID/workspaces
    #     /pces/:ID/modules
    #     /pces/:ID/module/:ID
    #     /pces/:ID/jobs
    #     /pces/:ID/jobs?user=ID&workspace=ID&module=ID
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @cherrypy.popargs('level')
    def GET(self, pce_id=None, level=None, level_id=None, **kwargs):
        prefix = '[GET /pces]'
        self.logger.debug(prefix)

        rtn = {}
        rtn['status'] = 0
        rtn['status_message'] = 'Success'


        valid_fns = self._get_is_valid_fns()


        #
        # Make sure the required fields have been specified
        #
        self.logger.debug(prefix + " Checking authorization")
        if 'apikey' not in kwargs.keys():
            self.logger.debug(prefix + " Authorization Failed: No 'apikey' specified")
            raise cherrypy.HTTPError(401)
        elif self._check_user_apikey(prefix, kwargs['apikey']) is False:
            self.logger.debug(prefix + " Authorization Failed: Invalid 'apikey' specified")
            raise cherrypy.HTTPError(401)
        self.logger.debug(prefix + " Authorization Success")


        #
        # Find correct functionality
        #
        if pce_id is not None:
            if valid_fns['pce'](pce_id) is False:
                raise cherrypy.HTTPError(400)

        #
        # /pces
        #
        if pce_id is None:
            self.logger.debug(prefix + " Processing...")

            pce_info = self._db.pce_get_info()
            if pce_info is None:
                self.logger.error(prefix + " Error no data found")
            else:
                self.logger.debug(prefix + " Package info for " + str(len(pce_info['data'])) + " pces")
                rtn['pces'] = pce_info

        #
        # /pces/:ID
        #
        elif level is None:
            prefix = prefix[:-1] + "/"+str(pce_id)+"]"
            self.logger.debug(prefix + " Processing...")

            pce_info = self._db.pce_get_info(pce_id)
            if pce_info is None:
                self.logger.error(prefix + " Error no data found")
            else:
                self.logger.debug(prefix + " Package info for " + str(len(pce_info['data'])) + " pces")
                rtn['pces'] = pce_info

        #
        # /pces/:ID/docs
        #
        elif level is not None and level == "docs":
            prefix = prefix[:-1] + "/"+str(pce_id)+"/"+level+"]"
            self.logger.debug(prefix + " Processing...")

            pce_info = self._db.pce_get_doc(pce_id)
            if pce_info is None:
                self.logger.error(prefix + " Error no data found")
            else:
                self.logger.debug(prefix + " Package info for " + str(len(pce_info)-1) + " pces")
                rtn['pces'] = pce_info

        #
        # /pces/:ID/workspaces
        #
        elif level is not None and level == "workspaces":
            prefix = prefix[:-1] + "/"+str(pce_id)+"/"+level+"]"
            self.logger.debug(prefix + " Processing...")

            pce_info = self._db.pce_get_workspaces(pce_id)
            if pce_info is None:
                self.logger.error(prefix + " Error no data found")
            else:
                self.logger.debug(prefix + " Package info for " + str(len(pce_info['data'])) + " workspaces")
                rtn['pces'] = pce_info

        #
        # /pces/:ID/module/:ID
        #
        elif level is not None and level == "module" and level_id is not None:
            prefix = prefix[:-1] + "/"+str(pce_id)+"/"+level+"/"+str(level_id)+"]"
            self.logger.debug(prefix + " Processing...")

            #
            # Find this PCE
            #
            if self._db.is_valid_pce_id(pce_id) is False:
                self.logger.info(prefix + " Invalid PCE ID " + str(pce_id))
                raise cherrypy.HTTPError(400)
            if pce_id in self._pces:
                self._pces[pce_id].check_connection()
            else:
                self._pces[pce_id] = onramppce.PCEAccess(self.logger, self._db, pce_id, self._tmp_dir)
                self._pces[pce_id].check_connection()

            #
            # Update from PCE
            #
            self._pces[pce_id].refresh_module_states(level_id)

            #
            # Pull from DB
            #
            pce_info = self._db.pce_get_modules(pce_id, level_id)
            if pce_info is None:
                self.logger.error(prefix + " Error no data found")
            else:
                self.logger.debug(prefix + " Package info for 1 module")
                rtn['pces'] = pce_info
                rtn['pces']['uioptions'] = self._pces[pce_id].get_module_uioptions(level_id, True)
                rtn['pces']['metadata'] = self._pces[pce_id].get_module_metadata(level_id, True)
        #
        # /pces/:ID/modules
        #
        elif level is not None and level == "modules":
            prefix = prefix[:-1] + "/"+str(pce_id)+"/"+level+"]"
            self.logger.debug(prefix + " Processing...")

            #
            # Find this PCE
            #
            if self._db.is_valid_pce_id(pce_id) is False:
                self.logger.info(prefix + " Invalid PCE ID " + str(pce_id))
                raise cherrypy.HTTPError(400)
            if pce_id in self._pces:
                self._pces[pce_id].check_connection()
            else:
                self._pces[pce_id] = onramppce.PCEAccess(self.logger, self._db, pce_id, self._tmp_dir)
                self._pces[pce_id].check_connection()

            #
            # Update from PCE
            #
            self._pces[pce_id].refresh_module_states()

            #
            # Pull from DB
            #
            pce_info = self._db.pce_get_modules(pce_id)
            if pce_info is None:
                self.logger.error(prefix + " Error no data found")
            else:
                self.logger.debug(prefix + " Package info for " + str(len(pce_info['data'])) + " modules")
                rtn['pces'] = pce_info
        #
        # /pces/:ID/jobs
        # /pces/:ID/jobs?user=ID&workspace=ID&module=ID
        #
        elif level is not None and level == "jobs":
            prefix = prefix[:-1] + "/"+str(pce_id)+"/"+level+"]"
            self.logger.debug(prefix + " Processing...")

            #
            # Process keys
            #
            allowed_search = ["apikey", "user", "workspace", "module", "state"]
            ids = {}
            debug = ""
            for key, value in kwargs.iteritems():
                self.logger.debug(prefix + " Key/Value (" + key + ", " + str(value) + ")")
                if key not in allowed_search:
                    raise cherrypy.HTTPError(400)
                elif key == "state":
                    ids[key] = value
                    if type(value) is list:
                        debug += "("+key+"="+ (",".join(value)) +")"
                    else:
                        debug += "("+key+"="+value+")"
                elif key != "apikey":
                    ids[key+"_id"] = value
                    debug += "("+key+"="+value+")"

            self.logger.debug(prefix + " Processing... " + debug)
            pce_info = self._db.pce_get_jobs(pce_id, ids)
            if pce_info is None:
                self.logger.error(prefix + " Error no data found")
            else:
                self.logger.debug(prefix + " Package info contains " + str(len(pce_info['data'])) + " jobs")
                rtn['pces'] = pce_info
        #
        # Unknown
        #
        else:
            raise cherrypy.HTTPError(400)


        #
        # Perform the correct operation
        #

        return rtn


    #
    # OPTIONS /pces/
    #
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def OPTIONS(self, **kwargs):
        prefix = '[OPTIONS /pces]'
        self.logger.debug(prefix)

        rtn = {}
        rtn['status'] = 0
        rtn['status_message'] = 'Success'

        rtn['pces'] = self._db.get_pce_states()

        return rtn


########################################################
# Modules
########################################################
class Modules(_ServerResourceBase):

    # GET /modules
    #     /modules/:ID
    #     /modules/:ID/docs
    #     /modules/:ID/pces
    #     /modules/:ID/jobs
    #     /modules/:ID/jobs?user=ID&workspace=ID&pce=ID
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @cherrypy.popargs('level')
    def GET(self, module_id=None, level=None, **kwargs):
        prefix = '[GET /modules]'
        self.logger.debug(prefix)

        rtn = {}
        rtn['status'] = 0
        rtn['status_message'] = 'Success'


        valid_fns = self._get_is_valid_fns()


        #
        # Make sure the required fields have been specified
        #
        self.logger.debug(prefix + " Checking authorization")
        if 'apikey' not in kwargs.keys():
            self.logger.debug(prefix + " Authorization Failed: No 'apikey' specified")
            raise cherrypy.HTTPError(401)
        elif self._check_user_apikey(prefix, kwargs['apikey']) is False:
            self.logger.debug(prefix + " Authorization Failed: Invalid 'apikey' specified")
            raise cherrypy.HTTPError(401)
        self.logger.debug(prefix + " Authorization Success")


        #
        # Find correct functionality
        #
        if module_id is not None:
            if valid_fns['module'](module_id) is False:
                raise cherrypy.HTTPError(400)

        #
        # /modules
        #
        if module_id is None:
            self.logger.debug(prefix + " Processing...")

            module_info = self._db.module_get_info()
            if module_info is None:
                self.logger.error(prefix + " Error no data found")
            else:
                self.logger.debug(prefix + " Package info for " + str(len(module_info['data'])) + " modules")
                rtn['modules'] = module_info

        #
        # /modules/:ID
        #
        elif level is None:
            prefix = prefix[:-1] + "/"+str(module_id)+"]"
            self.logger.debug(prefix + " Processing...")

            module_info = self._db.module_get_info(module_id)
            if module_info is None:
                self.logger.error(prefix + " Error no data found")
            else:
                self.logger.debug(prefix + " Package info for " + str(len(module_info)-1) + " modules")
                rtn['modules'] = module_info

        #
        # /modules/:ID/docs
        #
        elif level is not None and level == "docs":
            prefix = prefix[:-1] + "/"+str(module_id)+"/"+level+"]"
            self.logger.debug(prefix + " Processing...")

            module_info = self._db.module_get_doc(module_id)
            if module_info is None:
                self.logger.error(prefix + " Error no data found")
            else:
                self.logger.debug(prefix + " Package info for " + str(len(module_info)-1) + " docs")
                rtn['modules'] = module_info

        #
        # /modules/:ID/pces
        #
        elif level is not None and level == "pces":
            prefix = prefix[:-1] + "/"+str(module_id)+"/"+level+"]"
            self.logger.debug(prefix + " Processing...")

            module_info = self._db.module_get_pces(module_id)
            if module_info is None:
                self.logger.error(prefix + " Error no data found")
            else:
                self.logger.debug(prefix + " Package info for " + str(len(module_info['data'])) + " PCEs")
                rtn['modules'] = module_info

        #
        # /modules/:ID/jobs
        # /modules/:ID/jobs?user=ID&workspace=ID&pce=ID
        #
        elif level is not None and level == "jobs":
            prefix = prefix[:-1] + "/"+str(module_id)+"/"+level+"]"
            self.logger.debug(prefix + " Processing...")

            #
            # Process keys
            #
            allowed_search = ["apikey", "user", "workspace", "pce", "state"]
            ids = {}
            debug = ""
            for key, value in kwargs.iteritems():
                self.logger.debug(prefix + " Key/Value (" + key + ", " + str(value) + ")")
                if key not in allowed_search:
                    raise cherrypy.HTTPError(400)
                elif key == "state":
                    ids[key] = value
                    if type(value) is list:
                        debug += "("+key+"="+ (",".join(value)) +")"
                    else:
                        debug += "("+key+"="+value+")"
                elif key != "apikey":
                    ids[key+"_id"] = value
                    debug += "("+key+"="+value+")"

            self.logger.debug(prefix + " Processing... " + debug)
            module_info = self._db.module_get_jobs(module_id, ids)
            if module_info is None:
                self.logger.error(prefix + " Error no data found")
            else:
                self.logger.debug(prefix + " Package info contains " + str(len(module_info['data'])) + " jobs")
                rtn['modules'] = module_info
        #
        # Unknown
        #
        else:
            raise cherrypy.HTTPError(400)


        #
        # Perform the correct operation
        #

        return rtn

    #
    # OPTIONS /modules/
    #
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def OPTIONS(self, **kwargs):
        prefix = '[OPTIONS /modules]'
        self.logger.debug(prefix)

        rtn = {}
        rtn['status'] = 0
        rtn['status_message'] = 'Success'

        rtn['modules'] = self._db.get_module_states()

        return rtn

########################################################
# State translations
########################################################
class States(_ServerResourceBase):

    # GET /states/jobs
    #     /states/modules
    #     /states/pces
    #
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def GET(self, type_id, **kwargs):
        prefix = '[GET /states/'+type_id+']'
        self.logger.debug(prefix)

        rtn = {}
        rtn['status'] = 0
        rtn['status_message'] = 'Success'

        
        if type_id == "jobs":
            rtn[type_id] = self._db.get_job_states()
        elif type_id == "pces":
            rtn[type_id] = self._db.get_pce_states()
        elif type_id == "modules":
            rtn[type_id] = self._db.get_module_states()
        else:
            raise cherrypy.HTTPError(400)

        return rtn


########################################################
# Jobs
########################################################
class Jobs(_ServerResourceBase):

    # GET /jobs
    #     /jobs/:ID
    #     /jobs/:ID/data
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    @cherrypy.popargs('level')
    def GET(self, job_id=None, level=None, **kwargs):
        prefix = '[GET /jobs]'
        self.logger.debug(prefix)

        rtn = {}
        rtn['status'] = 0
        rtn['status_message'] = 'Success'


        valid_fns = self._get_is_valid_fns()


        #
        # Make sure the required fields have been specified
        #
        self.logger.debug(prefix + " Checking authorization")
        if 'apikey' not in kwargs.keys():
            self.logger.debug(prefix + " Authorization Failed: No 'apikey' specified")
            raise cherrypy.HTTPError(401)
        elif self._check_user_apikey(prefix, kwargs['apikey']) is False:
            self.logger.debug(prefix + " Authorization Failed: Invalid 'apikey' specified")
            raise cherrypy.HTTPError(401)
        self.logger.debug(prefix + " Authorization Success")


        #
        # Find correct functionality
        #
        if job_id is not None:
            if valid_fns['job'](job_id) is False:
                raise cherrypy.HTTPError(400)

        #
        # /jobs
        #
        if job_id is None:
            self.logger.debug(prefix + " Processing...")

            #
            # Process keys
            #
            allowed_search = ["apikey", "user", "workspace", "pce", "module", "state", "output_file"]
            ids = {}
            debug = ""
            for key, value in kwargs.iteritems():
                self.logger.debug(prefix + " Key/Value (" + key + ", " + str(value) + ")")
                if key not in allowed_search:
                    raise cherrypy.HTTPError(400)
                elif key == "state":
                    ids[key] = value
                    if type(value) is list:
                        debug += "("+key+"="+ (",".join(value)) +")"
                    else:
                        debug += "("+key+"="+value+")"
                elif key != "apikey":
                    ids[key+"_id"] = value
                    debug += "("+key+"="+value+")"

            self.logger.debug(prefix + " Processing..." + debug)

            job_info = self._db.job_get_info( search_params=ids )
            if job_info is None:
                self.logger.error(prefix + " Error no data found")
            else:
                self.logger.debug(prefix + " Package info for " + str(len(job_info['data'])) + " jobs")
                rtn['jobs'] = job_info

        #
        # /jobs/:ID
        #
        elif level is None:
            prefix = prefix[:-1] + "/"+str(job_id)+"]"
            self.logger.debug(prefix + " Processing...")

            #
            # Get PCE associated with this job
            #
            info = self._db.job_get_info(job_id)
            if info is None:
                self.logger.error(prefix + " Error no data found")
                raise cherrypy.HTTPError(400)

            job_info = dict( zip( info["fields"], info["data"] ) )
            pce_id = int( job_info["pce_id"] )

            self.logger.info(prefix + " Job ID " + str(job_id) + " running on PCE ID " + str(pce_id))

            #
            # Ask that PCE to update the job state
            #
            if self._db.is_valid_pce_id(pce_id) is False:
                self.logger.info(prefix + " Invalid PCE ID " + str(pce_id))
                raise cherrypy.HTTPError(400)

            if pce_id in self._pces:
                self._pces[pce_id].check_connection()
            else:
                self._pces[pce_id] = onramppce.PCEAccess(self.logger, self._db, pce_id, self._tmp_dir)
                self._pces[pce_id].check_connection()

            # Ask the PCE
            job_info = self._pces[pce_id].check_on_job( job_id )

            rtn['jobs'] = job_info

        #
        # /jobs/:ID/data
        #
        elif level is not None and level == "data":
            prefix = prefix[:-1] + "/"+str(job_id)+"]"
            self.logger.debug(prefix + " Processing...")

            #                                                                                                                    
            # Get PCE associated with this job                                                                                   
            #                                                                                                                    
            info = self._db.job_get_info(job_id)
            if info is None:
                self.logger.error(prefix + " Error no data found")
                raise cherrypy.HTTPError(400)

            job_info = dict( zip( info["fields"], info["data"] ) )
            pce_id = int( job_info["pce_id"] )

            self.logger.info(prefix + " Job ID " + str(job_id) + " running on PCE ID " + str(pce_id))

            #                                                                                                                    
            # Ask that PCE to update the job state                                                                               
            #                                                                                                                    
            if self._db.is_valid_pce_id(pce_id) is False:
                self.logger.info(prefix + " Invalid PCE ID " + str(pce_id))
                raise cherrypy.HTTPError(400)

            if pce_id in self._pces:
                self._pces[pce_id].check_connection()
            else:
                self._pces[pce_id] = onramppce.PCEAccess(self.logger, self._db, pce_id, self._tmp_dir)
                self._pces[pce_id].check_connection()

            # Ask the PCE                                                                                                        
            job_info = self._pces[pce_id].get_job_output(job_id)

            rtn['jobs'] = job_info

            
            #prefix = prefix[:-1] + "/"+str(job_id)+"/"+level+"]"
            #self.logger.debug(prefix + " Processing...")


            
            #job_info = self._db.job_get_data(job_id)
            #if job_info is None:
            #    self.logger.error(prefix + " Error no data found")
            #else:
            #    self.logger.debug(prefix + " Package info for " + str(len(job_info)-1) + " data")
            #    rtn['jobs'] = job_info

        #
        # Unknown
        #
        else:
            raise cherrypy.HTTPError(400)


        #
        # Perform the correct operation
        #

        return rtn

    #
    # POST /jobs
    #
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self, **kwargs):
        prefix = '[POST /jobs]'
        self.logger.debug(prefix)

        rtn = {}
        rtn['status'] = 0
        rtn['status_message'] = 'Success'


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
        # Try to launch the job
        #
        if 'info' not in data.keys():
            self.logger.error(prefix + " No job info sent")
            raise cherrypy.HTTPError(400)

        req_keys = ["user_id", "workspace_id", "pce_id", "module_id", "job_name"]
        for key in req_keys:
            if key not in data['info'].keys():
                self.logger.error(prefix + " Missing value '" + key + "'")
                raise cherrypy.HTTPError(400)

        user_id      = data['info']['user_id']
        workspace_id = data['info']['workspace_id']
        pce_id       = data['info']['pce_id']
        module_id    = data['info']['module_id']
        job_data = {}
        job_data["job_name"] = data['info']['job_name']
        job_data["uioptions"] = data['uioptions']

        #
        # Authorized to submit a job as this user? (Must be the user or an Admin)
        #
        if data['auth']['user_id'] != user_id:
            if self._check_auth(prefix, data['auth'], True, False) is False:
                self.logger.error(prefix + " Authorization Failed: User ID mismatch (" + str(data['auth']['user_id']) + " vs " + str(data['info']['user_id']) +")")
                raise cherrypy.HTTPError(401)
            else:
                self.logger.debug(prefix + " Admin submitting for user " + str(data['info']['user_id']) )


        #
        # Find this PCE
        #
        if self._db.is_valid_pce_id(pce_id) is False:
            self.logger.info(prefix + " Invalid PCE ID " + str(pce_id))
            raise cherrypy.HTTPError(400)

        if pce_id in self._pces:
            self._pces[pce_id].check_connection()
        else:
            self._pces[pce_id] = onramppce.PCEAccess(self.logger, self._db, pce_id, self._tmp_dir)
            self._pces[pce_id].check_connection()

        #
        # Try to launch the job
        #
        result = self._pces[pce_id].launch_a_job(user_id, workspace_id, module_id, job_data)
        if 'error_msg' in result.keys():
            self.logger.info(prefix + " " + rdata['error_msg'])
            raise cherrypy.HTTPError(400)

        rtn['job'] = result

        #
        # Return information about the submission
        #
        return rtn

    #
    # OPTIONS /jobs/
    #
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def OPTIONS(self, **kwargs):
        prefix = '[OPTIONS /jobs]'
        self.logger.debug(prefix)

        rtn = {}
        rtn['status'] = 0
        rtn['status_message'] = 'Success'

        rtn['jobs'] = self._db.get_job_states()

        return rtn

    #
    # DELETE /jobs/:ID
    #
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def DELETE(self, id, **kwargs):
        prefix = '[DELETE /jobs]'
        self.logger.debug(prefix)

        rtn = {}
        rtn['status'] = 0
        rtn['status_message'] = 'Success'

        return self._not_implemented(prefix)

        return rtn


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

        user_auth = self._db.user_login( data["username"], data["password"])
        
        if user_auth is None:
            self.logger.info(prefix + " Attempt \"" + data["username"] + "\" Failed")
            raise cherrypy.HTTPError(401)
        else:
            rtn['auth'] = user_auth
            rtn['auth']['username'] = data["username"]
            self.logger.info(prefix + " Attempt \"" + data["username"] + "\" Success")


        #
        # Tell the user
        #

        return rtn

########################################################
# Logout
########################################################
class Logout(_ServerResourceBase):

    # POST /logout
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self, id=None, **kwargs):
        prefix = '[POST /logout]'
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
        self.logger.debug(prefix + " Checking authorization")
        if 'auth' not in data.keys():
            self.logger.debug(prefix + " Authorization Failed: No 'auth' key")
            raise cherrypy.HTTPError(401)
        #
        # Ask the database if this is a valid user
        #
        elif self._check_auth(prefix, data['auth'] ) is True:
            self.logger.debug(prefix + " Authorization Success")

        val = self._db.user_logout( data["auth"] )

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
        elif self._check_auth(prefix, data['auth'], True) is True:
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
            rdata = self._db.user_add_if_new( data["username"], data["password"] )
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
            rdata = self._db.workspace_add_if_new( data["name"] )
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
            rdata = self._db.workspace_add_user( workspace_id, user_id )
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
            rdata = self._db.workspace_add_pair( workspace_id, pce_id, module_id )
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
            rdata = self._db.pce_add_if_new( data )
            pce_id = rdata['id']

            #
            # Connect to the PCE
            #
            if rdata['exists'] is True:
                self._pces[pce_id].check_connection()
            else:
                self._pces[pce_id] = onramppce.PCEAccess(self.logger, self._db, pce_id, self._tmp_dir)
                self._pces[pce_id].establish_connection()

            rdata['state'] = self._db.pce_get_state(pce_id)
        #
        # Associate a module with a PCE (trigger deployment)
        # /admin/pce/:PCEID/module/:MODULEID
        #
        elif level2 is not None and level2 == "module" and level2_id is not None and level3_id is None:
            module_id = level2_id
            prefix = prefix[:-1] + "/" + str(pce_id) + "/module/" + str(module_id) + "]"
            self.logger.info(prefix + " Associate module " + str(module_id) + " with PCE "+str(pce_id))

            #
            # Find this PCE
            #
            if self._db.is_valid_pce_id(pce_id) is False:
                self.logger.info(prefix + " Invalid PCE ID " + str(pce_id))
                raise cherrypy.HTTPError(400)
            if pce_id in self._pces:
                self._pces[pce_id].check_connection()
            else:
                self._pces[pce_id] = onramppce.PCEAccess(self.logger, self._db, pce_id, self._tmp_dir)
                self._pces[pce_id].check_connection()

            #
            # Add the module to the PCE
            #
            rdata = self._pces[pce_id].install_and_deploy_module(int(module_id))
            if 'error_msg' in rdata.keys():
                self.logger.info(prefix + " " + rdata['error_msg'])
                raise cherrypy.HTTPError(400)

            #
            # Return the state of the module to the user
            #
            rdata = self._db.pce_get_modules(pce_id, module_id)
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
            rdata = self._db.module_add_if_new( data["name"] )
            module_id = rdata['id']
        #
        # Note implemented
        #
        else:
            raise cherrypy.NotFound()

        self.logger.debug(prefix + ' process_module(%s, %s)' % (type, module_id))

        return rdata

