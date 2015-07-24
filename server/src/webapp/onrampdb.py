"""Functionality to support interacting with an OnRamp Database

"""

import os
import json
import exceptions

class Database():

    job_states = { 0 : "Not on PCE",
                   1 : "On PCE",
                   2 : "On PCE Preprocess",
                   3 : "On PCE Queued",
                   4 : "On PCE Postprocess",
                   5 : "Finished",
                  -1 : "Error: Undefined",
                  }

    def __init__(self, logger, auth):
        self._auth = auth
        self._logger = logger

    def is_connected(self):
        raise NotImplemented("Please implement this method")

    def connect(self):
        raise NotImplemented("Please implement this method")

    def disconnect(self):
        raise NotImplemented("Please implement this method")


    ##########################################################
    def is_valid_session_id(self, session_id):
        raise NotImplemented("Please implement this method")

    def is_valid_user_id(self, user_id):
        raise NotImplemented("Please implement this method")

    def is_valid_workspace_id(self, workspace_id):
        raise NotImplemented("Please implement this method")

    def is_valid_pce_id(self, pce_id):
        raise NotImplemented("Please implement this method")

    def is_valid_module_id(self, module_id):
        raise NotImplemented("Please implement this method")

    def is_valid_job_id(self, job_id):
        raise NotImplemented("Please implement this method")

    def is_valid_user_workspace(self, user_id, workspace_id):
        raise NotImplemented("Please implement this method")

    def is_valid_pce_module(self, pce_id, module_id):
        raise NotImplemented("Please implement this method")

    def is_valid_workspace_pce_module(self, workspace_id, pce_id, module_id):
        raise NotImplemented("Please implement this method")

    ##########################################################
    def is_active_session_id(self, session_id, user_id=None):
        raise NotImplemented("Please implement this method")

    def session_start(self, user_id):
        raise NotImplemented("Please implement this method")

    def session_update(self, session_id):
        raise NotImplemented("Please implement this method")

    def session_stop(self, session_id):
        raise NotImplemented("Please implement this method")

    ##########################################################
    def get_user_id(self, req_admin, username, password=None):
        raise NotImplemented("Please implement this method")

    def add_user(self, username, password):
        raise NotImplemented("Please implement this method")

    def get_user_info(self, user_id=None):
        raise NotImplemented("Please implement this method")

    def get_user_workspaces(self, user_id):
        raise NotImplemented("Please implement this method")

    def get_user_jobs(self, user_id, search_params):
        raise NotImplemented("Please implement this method")

    ##########################################################
    def get_workspace_id(self, name):
        raise NotImplemented("Please implement this method")

    def add_workspace(self, name):
        raise NotImplemented("Please implement this method")

    def lookup_user_in_workspace(self, workspace_id, user_id):
        raise NotImplemented("Please implement this method")

    def add_user_to_workspace(self, workspace_id, user_id):
        raise NotImplemented("Please implement this method")

    def lookup_pair_in_workspace(self, workspace_id, pm_pair_id):
        raise NotImplemented("Please implement this method")

    def add_pair_to_workspace(self, workspace_id, pm_pair_id):
        raise NotImplemented("Please implement this method")

    ##########################################################
    def get_pce_id(self, name):
        raise NotImplemented("Please implement this method")

    def add_pce(self, name):
        raise NotImplemented("Please implement this method")

    def lookup_module_in_pce(self, pce_id, module_id):
        raise NotImplemented("Please implement this method")

    def add_module_to_pce(self, pce_id, module_id):
        raise NotImplemented("Please implement this method")

    ##########################################################
    def get_module_id(self, name):
        raise NotImplemented("Please implement this method")

    def add_module(self, name):
        raise NotImplemented("Please implement this method")

    ##########################################################
    def find_job_id(self, user_id, workspace_id, pce_id, module_id, job_name):
        raise NotImplemented("Please implement this method")

    def add_job(self, user_id, workspace_id, pce_id, module_id, job_data):
        raise NotImplemented("Please implement this method")

    ##########################################################

    

from webapp.onrampdb_sqlite import Database_sqlite

##########################################
class DBAccess():
    _known_db = { 'sqlite' : Database_sqlite }

    ##########################################
    def __init__(self, logger, dbtype, auth):
        self._logger = logger
        if dbtype not in self._known_db:
            self._logger.critical( "Database: \"%s\" is not supported." % (dbtype) )
            raise NotImplementedError

        self._db = self._known_db[dbtype](logger, auth)


    def get_job_states(self):
        return self._db.job_states

    ##########################################
    # Valid keys
    ##########################################
    def is_valid_user_id(self, user_id):
        self._db.connect()
        result = self._db.is_valid_user_id(user_id)
        self._db.disconnect()
        return result

    def is_valid_workspace_id(self, workspace_id):
        self._db.connect()
        result = self._db.is_valid_workspace_id(workspace_id)
        self._db.disconnect()
        return result

    def is_valid_pce_id(self, pce_id):
        self._db.connect()
        result = self._db.is_valid_pce_id(pce_id)
        self._db.disconnect()
        return result

    def is_valid_module_id(self, module_id):
        self._db.connect()
        result = self._db.is_valid_module_id(module_id)
        self._db.disconnect()
        return result

    def is_valid_job_id(self, job_id):
        self._db.connect()
        result = self._db.is_valid_job_id(job_id)
        self._db.disconnect()
        return result

    def is_valid_user_workspace(self, user_id, workspace_id):
        self._db.connect()
        result = self._db.is_valid_user_workspace(user_id, workspace_id)
        self._db.disconnect()
        return result

    def is_valid_pce_module(self, pce_id, module_id):
        self._db.connect()
        result = self._db.is_valid_pce_module(pce_id, module_id)
        self._db.disconnect()
        return result

    def is_valid_workspace_pce_module(self, workspace_id, pce_id, module_id):
        self._db.connect()
        result = self._db.is_valid_workspace_pce_module(workspace_id, pce_id, module_id)
        self._db.disconnect()
        return result

    ##########################################
    # User Management
    ##########################################
    def user_login(self, username, password):
        self._db.connect()
        user_id = self._db.get_user_id(False, username, password)
        session_id = self._db.session_start(user_id)
        self._db.disconnect()
        # TODO create a real apikey tied to this session
        return {'user_id': user_id, 'session_id': session_id, 'apikey' : session_id}

    def user_update(self, auth ):
        self._db.connect()
        self._db.session_update( auth['session_id'] )
        self._db.disconnect()
        return True

    def user_logout(self, auth ):
        self._db.connect()
        self._db.session_stop( auth['session_id'] )
        self._db.disconnect()
        return True

    def check_user_apikey(self, apikey ):
        self._db.connect()
        result = self._db.is_active_session_id( apikey )
        self._db.disconnect()

        return result

    def check_user_auth(self, auth, req_admin=False ):
        req_keys = ["session_id", "username", "user_id"]
        for key in req_keys:
            if key not in auth.keys():
                return False

        user_id = self.user_lookup( auth['username'], req_admin=req_admin )
        # Username does not exist
        if user_id is None:
            return False
        # ID mismatch
        elif user_id != auth['user_id']:
            return False
        # Session inactive -- TODO
        else:
            self._db.connect()
            result = self._db.is_active_session_id(auth['session_id'], auth['user_id'])
            self._db.disconnect()
            return result

        return True

    ##########################################
    def user_add_if_new(self, username, password):
        self._db.connect()

        info = {}

        user_id = self._db.get_user_id(False, username)
        if user_id is not None:
            info['exists'] = True
        else:
            info['exists'] = False
            user_id = self._db.add_user(username, password)

        info['id'] = user_id

        self._db.disconnect()
        return info

    ##########################################
    def user_lookup(self, username, req_admin=False):
        self._db.connect()
        user_id = self._db.get_user_id(req_admin, username)
        self._db.disconnect()
        return user_id

    ##########################################
    def user_add(self, username, password):
        self._db.connect()
        user_id = self._db.add_user(username, password)
        self._db.disconnect()
        return user_id

    ##########################################
    def user_get_info(self, user_id=None):
        self._db.connect()

        if user_id is not None and self._db.is_valid_user_id(user_id) is False:
            self._logger.error("Invalid User ID ("+str(user_id)+")")
            self._db.disconnect()
            return None

        user_info = self._db.get_user_info(user_id)
        self._db.disconnect()
        return user_info

    ##########################################
    def user_get_workspaces(self, user_id):
        self._db.connect()

        if self._db.is_valid_user_id(user_id) is False:
            self._logger.error("Invalid User ID ("+str(user_id)+")")
            self._db.disconnect()
            return None

        user_info = self._db.get_user_workspaces(user_id)
        self._db.disconnect()
        return user_info

    ##########################################
    def user_get_jobs(self, user_id, search_params={}):
        self._db.connect()

        if self._db.is_valid_user_id(user_id) is False:
            self._logger.error("Invalid User ID ("+str(user_id)+")")
            self._db.disconnect()
            return None

        user_info = self._db.get_user_jobs(user_id, search_params)
        self._db.disconnect()
        return user_info
    

    ##########################################
    # Workspace Management
    ##########################################
    def workspace_add_if_new(self, name):
        self._db.connect()

        info = {}

        workspace_id = self._db.get_workspace_id(name)
        if workspace_id is not None:
            info['exists'] = True
        else:
            info['exists'] = False
            workspace_id = self._db.add_workspace(name)

        info['id'] = workspace_id

        self._db.disconnect()
        return info

    ##########################################
    def workspace_lookup(self, name):
        self._db.connect()
        work_id = self._db.get_workspace_id(name)
        self._db.disconnect()
        return work_id

    ##########################################
    def workspace_add(self, name):
        self._db.connect()
        work_id = self._db.add_workspace(name)
        self._db.disconnect()
        return work_id

    ##########################################
    def workspace_add_user(self, workspace_id, user_id):
        self._db.connect()

        info = {}

        if self._db.is_valid_workspace_id(workspace_id) is False:
            info['error_msg'] = "Invalid Workspace ID ("+str(workspace_id)+")"
            self._db.disconnect()
            return info

        if self._db.is_valid_user_id(user_id) is False:
            info['error_msg'] = "Invalid User ID ("+str(user_id)+")"
            self._db.disconnect()
            return info

        pair_id = self._db.lookup_user_in_workspace(workspace_id, user_id)
        if pair_id is not None:
            info['exists'] = True
        else:
            info['exists'] = False
            pair_id = self._db.add_user_to_workspace(workspace_id, user_id)

        info['id'] = pair_id

        self._db.disconnect()
        return info

    ##########################################
    def workspace_add_pair(self, workspace_id, pce_id, module_id):
        self._db.connect()

        info = {}

        if self._db.is_valid_workspace_id(workspace_id) is False:
            info['error_msg'] = "Invalid Workspace ID ("+str(workspace_id)+")"
            self._db.disconnect()
            return info

        pm_pair_id = self._db.lookup_module_in_pce(pce_id, module_id)
        if pm_pair_id is None:
            info['error_msg'] = "Invalid Module / PCE Pair (module="+str(module_id)+", pce="+str(pce_id)+")"
            self._db.disconnect()
            return info

        pair_id = self._db.lookup_pair_in_workspace(workspace_id, pm_pair_id)
        if pair_id is not None:
            info['exists'] = True
        else:
            info['exists'] = False
            pair_id = self._db.add_pair_to_workspace(workspace_id, pm_pair_id)

        info['id'] = pair_id

        self._db.disconnect()
        return info


    ##########################################
    # PCE Management
    ##########################################
    def pce_add_if_new(self, name):
        self._db.connect()

        info = {}

        pce_id = self._db.get_pce_id(name)
        if pce_id is not None:
            info['exists'] = True
        else:
            info['exists'] = False
            pce_id = self._db.add_pce(name)

        info['id'] = pce_id

        self._db.disconnect()
        return info

    ##########################################
    def pce_lookup(self, name):
        self._db.connect()
        pce_id = self._db.get_pce_id(name)
        self._db.disconnect()
        return pce_id

    ##########################################
    def pce_add(self, name):
        self._db.connect()
        pce_id = self._db.add_pce(name)
        self._db.disconnect()
        return pce_id

    ##########################################
    def pce_add_module(self, pce_id, module_id ):
        self._db.connect()

        info = {}

        if self._db.is_valid_pce_id(pce_id) is False:
            info['error_msg'] = "Invalid PCE ID ("+str(pce_id)+")"
            self._db.disconnect()
            return info

        if self._db.is_valid_module_id(module_id) is False:
            info['error_msg'] = "Invalid Module ID ("+str(module_id)+")"
            self._db.disconnect()
            return info

        pair_id = self._db.lookup_module_in_pce(pce_id, module_id)
        if pair_id is not None:
            info['exists'] = True
        else:
            info['exists'] = False
            pair_id = self._db.add_module_to_pce(pce_id, module_id)

        info['id'] = pair_id

        self._db.disconnect()
        return info


    ##########################################
    # Module Management
    ##########################################
    def module_add_if_new(self, name):
        self._db.connect()

        info = {}

        module_id = self._db.get_module_id(name)
        if module_id is not None:
            info['exists'] = True
        else:
            info['exists'] = False
            module_id = self._db.add_module(name)

        info['id'] = module_id

        self._db.disconnect()
        return info

    ##########################################
    def module_lookup(self, name):
        self._db.connect()
        module_id = self._db.get_module_id(name)
        self._db.disconnect()
        return module_id

    ##########################################
    def module_add(self, name):
        self._db.connect()
        module_id = self._db.add_module(name)
        self._db.disconnect()
        return module_id

    ##########################################
    # Job Management
    ##########################################
    def job_add(self, user_id, workspace_id, pce_id, module_id, job_data):
        self._db.connect()

        # See if already exists
        job_id = self._db.find_job_id(user_id, workspace_id, pce_id, module_id, job_data['job_name'])
        if job_id is not None:
            return (True, job_id)

        # Make sure this is a good tuple (allowed to submit the job)
        # Check: The User is in the Workspace
        if self._db.is_valid_user_workspace(user_id, workspace_id) is False:
            self._logger.error("Invalid User ID ("+str(user_id)+") and Workspace ID ("+str(workspace_id)+") combo")
            self._db.disconnect()
            return None

        # Check: The Workspace is allowed to interact with this PCE / Module pair
        if self._db.is_valid_workspace_pce_module(workspace_id, pce_id, module_id) is False:
            self._logger.error("Invalid Workspace / PCE / Module Combo ("+str(workspace_id)+" / "+str(pce_id)+" / "+str(module_id)+")")
            self._db.disconnect()
            return None

        # Log the job
        job_id = self._db.add_job(user_id, workspace_id, pce_id, module_id, job_data)

        self._db.disconnect()
        return (False, job_id)
