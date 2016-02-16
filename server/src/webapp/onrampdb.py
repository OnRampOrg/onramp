"""Functionality to support interacting with an OnRamp Database

"""

import os
import json
import exceptions

class Database():

    # JJH TODO Need a reverse lookup

    pce_states    = { 0 : "Running",
                      1 : "Establishing Connection",
                      2 : "Down",
                      -1 : "Error: Undefined",
                      }

    module_states = {  0 : "Not on PCE",
                       1 : "Available on PCE, Not Installed",
                       2 : "Checkout in progress",
                      -2 : "Error: Checkout failed",
                       3 : "Available on PCE, Installed, Not Deployed",
                       4 : "Available on PCE, Deploying",
                      -4 : "Error: Deploy failed",
                       5 : "Available on PCE, Deploy wait for admin",
                       6 : "Available on PCE, Deployed",
                      -99 : "Error: Undefined",
                      }

    job_states = {  0 : "Unknown job id",
                    1 : "Setting up launch",
                   -1 : "Launch failed",
                    2 : "Preprocessing",
                   -2 : "Preprocess failed",
                    3 : "Scheduled",
                   -3 : "Schedule failed",
                    4 : "Queued",
                    5 : "Running",
                   -5 : "Run failed",
                    6 : "Postprocessing",
                    7 : "Done",
                   -99 : "Error: Undefined",
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

    def get_workspace_info(self, workspace_id=None):
        raise NotImplemented("Please implement this method")

    def get_workspace_doc(self, workspace_id):
        raise NotImplemented("Please implement this method")

    def get_workspace_users(self, workspace_id):
        raise NotImplemented("Please implement this method")

    def get_workspace_pairs(self, workspace_id):
        raise NotImplemented("Please implement this method")

    def get_workspace_jobs(self, workspace_id, search_params):
        raise NotImplemented("Please implement this method")

    ##########################################################
    def get_all_pce_ids(self):
        raise NotImplemented("Please implement this method")

    def get_pce_id(self, info):
        raise NotImplemented("Please implement this method")

    def add_pce(self, info):
        raise NotImplemented("Please implement this method")

    def lookup_module_in_pce(self, pce_id, module_id):
        raise NotImplemented("Please implement this method")

    def add_module_to_pce(self, pce_id, module_id, src_location_type='local', src_location_path=''):
        raise NotImplemented("Please implement this method")

    def update_pce_module_state(self, pce_id, module_id, state):
        raise NotImplemented("Please implement this method")

    def get_pce_info(self, pce_id=None):
        raise NotImplemented("Please implement this method")

    def get_pce_state(self, pce_id):
        raise NotImplemented("Please implement this method")

    def update_pce_state(self, pce_id, state):
        raise NotImplemented("Please implement this method")

    def get_pce_doc(self, pce_id):
        raise NotImplemented("Please implement this method")

    def get_pce_workspaces(self, pce_id):
        raise NotImplemented("Please implement this method")

    def get_pce_modules(self, pce_id, module_id=None):
        raise NotImplemented("Please implement this method")

    def get_pce_jobs(self, pce_id, search_params):
        raise NotImplemented("Please implement this method")

    ##########################################################
    def get_module_id(self, name):
        raise NotImplemented("Please implement this method")

    def add_module(self, name):
        raise NotImplemented("Please implement this method")

    def get_module_info(self, module_id=None):
        raise NotImplemented("Please implement this method")

    def get_module_doc(self, module_id):
        raise NotImplemented("Please implement this method")

    def get_module_pces(self, module_id):
        raise NotImplemented("Please implement this method")

    def get_module_jobs(self, module_id, search_params):
        raise NotImplemented("Please implement this method")

    ##########################################################
    def find_job_id(self, user_id, workspace_id, pce_id, module_id, job_name):
        raise NotImplemented("Please implement this method")

    def add_job(self, user_id, workspace_id, pce_id, module_id, job_data):
        raise NotImplemented("Please implement this method")

    def get_job_info(self, module_id=None, search_params={}):
        raise NotImplemented("Please implement this method")

    def get_job_data(self, job_id):
        raise NotImplemented("Please implement this method")

    def update_job_state(self, job_id, state):
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


    ##########################################
    # State translations
    ##########################################
    def get_pce_state_str(self, id):
        if id not in self._db.pce_states:
            return None
        return self._db.pce_states[id]

    def get_pce_states(self):
        return self._db.pce_states

    def get_module_state_str(self, id):
        if id not in self._db.module_states:
            return None
        return self._db.module_states[id]

    def get_module_states(self):
        return self._db.module_states

    def get_job_state_str(self, id):
        if id not in self._db.job_states:
            return None
        return self._db.job_states[id]

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
        if user_id is None:
            self._db.disconnect()
            return None
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
    def workspace_get_info(self, workspace_id=None):
        self._db.connect()

        if workspace_id is not None and self._db.is_valid_workspace_id(workspace_id) is False:
            self._logger.error("Invalid Workspace ID ("+str(workspace_id)+")")
            self._db.disconnect()
            return None

        workspace_info = self._db.get_workspace_info(workspace_id)
        self._db.disconnect()
        return workspace_info

    ##########################################
    def workspace_get_doc(self, workspace_id):
        self._db.connect()

        if workspace_id is not None and self._db.is_valid_workspace_id(workspace_id) is False:
            self._logger.error("Invalid Workspace ID ("+str(workspace_id)+")")
            self._db.disconnect()
            return None

        workspace_info = self._db.get_workspace_doc(workspace_id)
        self._db.disconnect()
        return workspace_info

    ##########################################
    def workspace_get_users(self, workspace_id):
        self._db.connect()

        if workspace_id is not None and self._db.is_valid_workspace_id(workspace_id) is False:
            self._logger.error("Invalid Workspace ID ("+str(workspace_id)+")")
            self._db.disconnect()
            return None

        workspace_info = self._db.get_workspace_users(workspace_id)
        self._db.disconnect()
        return workspace_info

    ##########################################
    def workspace_get_pairs(self, workspace_id):
        self._db.connect()

        if workspace_id is not None and self._db.is_valid_workspace_id(workspace_id) is False:
            self._logger.error("Invalid Workspace ID ("+str(workspace_id)+")")
            self._db.disconnect()
            return None

        workspace_info = self._db.get_workspace_pairs(workspace_id)
        self._db.disconnect()
        return workspace_info

    ##########################################
    def workspace_get_jobs(self, workspace_id, search_params={}):
        self._db.connect()

        if self._db.is_valid_workspace_id(workspace_id) is False:
            self._logger.error("Invalid Workspace ID ("+str(workspace_id)+")")
            self._db.disconnect()
            return None

        workspace_info = self._db.get_workspace_jobs(workspace_id, search_params)
        self._db.disconnect()
        return workspace_info


    ##########################################
    # PCE Management
    ##########################################
    def pce_get_all_ids(self):
        self._db.connect()
        info = self._db.get_all_pce_ids()
        self._db.disconnect()
        return info

    def pce_add_if_new(self, data):
        self._db.connect()

        info = {}

        pce_id = self._db.get_pce_id(data)
        if pce_id is not None:
            info['exists'] = True
        else:
            info['exists'] = False
            pce_id = self._db.add_pce(data)

        pce_state = self._db.get_pce_state(pce_id)

        info['id'] = pce_id
        info['state'] = pce_state

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
    def pce_add_module(self, pce_id, module_id, src_location_type='local', src_location_path='' ):
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
            pair_id = self._db.add_module_to_pce(pce_id, module_id, src_location_type, src_location_path)

        info['id'] = pair_id

        self._db.disconnect()
        return info

    ##########################################
    def pce_update_module_state(self, pce_id, module_id, state):
        self._db.connect()

        pm_pair_id = self._db.lookup_module_in_pce(pce_id, module_id)
        if pm_pair_id is None:
            self._logger.error("Invalid Module / PCE Pair (module="+str(module_id)+", pce="+str(pce_id)+")")
            self._db.disconnect()
            return None

        pce_info = self._db.update_pce_module_state(pce_id, module_id, state)
        self._db.disconnect()
        return pce_info


    ##########################################
    def pce_get_info(self, pce_id=None):
        self._db.connect()

        if pce_id is not None and self._db.is_valid_pce_id(pce_id) is False:
            self._logger.error("Invalid PCE ID ("+str(pce_id)+")")
            self._db.disconnect()
            return None

        pce_info = self._db.get_pce_info(pce_id)
        self._db.disconnect()
        return pce_info

    ##########################################
    def pce_get_state(self, pce_id):
        self._db.connect()

        if pce_id is not None and self._db.is_valid_pce_id(pce_id) is False:
            self._logger.error("Invalid PCE ID ("+str(pce_id)+")")
            self._db.disconnect()
            return None

        pce_state = self._db.get_pce_state(pce_id)
        self._db.disconnect()
        return pce_state

    ##########################################
    def pce_update_state(self, pce_id, state):
        self._db.connect()

        if pce_id is not None and self._db.is_valid_pce_id(pce_id) is False:
            self._logger.error("Invalid PCE ID ("+str(pce_id)+")")
            self._db.disconnect()
            return None

        if state not in self._db.pce_states:
            self._logger.error("Invalid PCE State ("+str(state)+")")
            self._db.disconnect()
            return None

        pce_info = self._db.update_pce_state(pce_id, state)
        self._db.disconnect()
        return pce_info

    ##########################################
    def pce_get_doc(self, pce_id):
        self._db.connect()

        if pce_id is not None and self._db.is_valid_pce_id(pce_id) is False:
            self._logger.error("Invalid Pce ID ("+str(pce_id)+")")
            self._db.disconnect()
            return None

        pce_info = self._db.get_pce_doc(pce_id)
        self._db.disconnect()
        return pce_info

    ##########################################
    def pce_get_workspaces(self, pce_id):
        self._db.connect()

        if pce_id is not None and self._db.is_valid_pce_id(pce_id) is False:
            self._logger.error("Invalid Pce ID ("+str(pce_id)+")")
            self._db.disconnect()
            return None

        pce_info = self._db.get_pce_workspaces(pce_id)
        self._db.disconnect()
        return pce_info

    ##########################################
    def pce_get_modules(self, pce_id, module_id = None):
        self._db.connect()

        if pce_id is not None and self._db.is_valid_pce_id(pce_id) is False:
            self._logger.error("Invalid Pce ID ("+str(pce_id)+")")
            self._db.disconnect()
            return None

        pce_info = self._db.get_pce_modules(pce_id, module_id)

        # Add the string representation of each of the module states
        pce_info["fields"] = list(pce_info["fields"])
        pce_info["fields"].append("state_str")

        self._logger.debug("module_id ("+str(module_id)+")")
        if module_id is None:
            data = []
            for m in pce_info["data"]:
                m = list(m)
                sstr = self.get_module_state_str( m[2] )
                m.append( sstr )
                data.append(m)
            pce_info["data"] = data
        else:
            pce_info["data"] = list(pce_info["data"])
            pce_info["data"].append( self.get_module_state_str( pce_info["data"][2] ) )

        self._db.disconnect()
        return pce_info

    ##########################################
    def pce_get_jobs(self, pce_id, search_params={}):
        self._db.connect()

        if pce_id is not None and self._db.is_valid_pce_id(pce_id) is False:
            self._logger.error("Invalid Pce ID ("+str(pce_id)+")")
            self._db.disconnect()
            return None

        pce_info = self._db.get_pce_jobs(pce_id, search_params)
        self._db.disconnect()
        return pce_info


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
        return int(module_id)

    ##########################################
    def module_add(self, name):
        self._db.connect()
        module_id = self._db.add_module(name)
        self._db.disconnect()
        return module_id

    ##########################################
    def module_get_info(self, module_id=None):
        self._db.connect()

        if module_id is not None and self._db.is_valid_module_id(module_id) is False:
            self._logger.error("Invalid Module ID ("+str(module_id)+")")
            self._db.disconnect()
            return None

        module_info = self._db.get_module_info(module_id)
        self._db.disconnect()
        return module_info

    ##########################################
    def module_get_doc(self, module_id):
        self._db.connect()

        if module_id is not None and self._db.is_valid_module_id(module_id) is False:
            self._logger.error("Invalid Module ID ("+str(module_id)+")")
            self._db.disconnect()
            return None

        module_info = self._db.get_module_doc(module_id)
        self._db.disconnect()
        return module_info

    ##########################################
    def module_get_pces(self, module_id):
        self._db.connect()

        if module_id is not None and self._db.is_valid_module_id(module_id) is False:
            self._logger.error("Invalid Module ID ("+str(module_id)+")")
            self._db.disconnect()
            return None

        module_info = self._db.get_module_pces(module_id)
        self._db.disconnect()
        return module_info

    ##########################################
    def module_get_jobs(self, module_id, search_params={}):
        self._db.connect()

        if module_id is not None and self._db.is_valid_module_id(module_id) is False:
            self._logger.error("Invalid Module ID ("+str(module_id)+")")
            self._db.disconnect()
            return None

        module_info = self._db.get_module_jobs(module_id, search_params)
        self._db.disconnect()
        return module_info

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

    ##########################################
    def job_get_info(self, job_id=None, search_params={}):
        self._db.connect()

        if job_id is not None and self._db.is_valid_job_id(job_id) is False:
            self._logger.error("Invalid Job ID ("+str(job_id)+")")
            self._db.disconnect()
            return None

        job_info = self._db.get_job_info(job_id, search_params)
        self._db.disconnect()
        return job_info

    ##########################################
    def job_get_data(self, job_id ):
        self._db.connect()

        if self._db.is_valid_job_id(job_id) is False:
            self._logger.error("Invalid Job ID ("+str(job_id)+")")
            self._db.disconnect()
            return None

        job_info = self._db.get_job_data(job_id)
        self._db.disconnect()
        return job_info

    ##########################################
    def job_update_state(self, job_id, state ):
        self._db.connect()

        if self._db.is_valid_job_id(job_id) is False:
            self._logger.error("Invalid Job ID ("+str(job_id)+")")
            self._db.disconnect()
            return None

        job_info = self._db.update_job_state(job_id, state)
        self._db.disconnect()
        return job_info

