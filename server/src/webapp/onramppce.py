"""Functionality to support interacting with an OnRamp PCE

"""

import os
import json
import requests

class PCEAccess():
    _name = "[PCEAccess] "

    def __init__(self, logger, dbaccess, pce_id):
        self._logger = logger
        self._db     = dbaccess
        self._pce_id = pce_id

        #
        # Get the PCE server information
        #
        pce_info = self._db.pce_get_info(pce_id)
        self._url = "http://%s:%d" % (pce_info['data'][2], pce_info['data'][3])

    def _pce_get(endpoint, **kwargs):
        s = requests.Sesssion()
        url = "%s/%s" % (self._url, endpoint)
        r = s.get(url, params=kwargs)

        if r.status_code != 200:
            self._logger.error(self._name + " Error: " + str(r.status_code)
                               + " from GET " + url + ": " + str(r.status_msg))
            return None
        else:
            return r.json()

    def _pce_post(endpoint, **kwargs):
        s = requests.Session()
        url = "%s/%s" % (self._url, endpoint)
        data = json.dumps(kwargs)
        headers = {"content-type": "application/json"}
        r = s.post(url, data=data, headers=headers)

        if r.status_code != 200:
            self._logger.error(self._name + " Error: " + str(r.status_code)
                               + " from GET " + url + ": " + str(r.status_msg))
            return None
        else:
            return r.json()

    def _pce_get_modules_avail():
        return self._rce_get("modules", state="Available")

    def _pce_get_modules(id=None):
        s = requests.Session()
        url = "modules"
        if id:
            url += "/%d" % id
        return self._pce_get(url)

    def _pce_add_module(id, module_name, mod_type, mod_path):
        payload = {
            'mod_id': id,
            'mod_name': module_name,
            'source_location': {
                'type': mod_type,
                'path': mod_path
            }
        }
        return self._pce_post("modules", **payload)

    def _pce_deploy_module(id):
        endpoint = "modules/%d" % id
        return self._pce_post(endpoint)

    def _pce_get_jobs(id=None):
        s = requests.Session()
        url = "jobs"
        if id:
            url += "/%d" % id
        return self._pce_get(url)

    def _pce_launch_job(user, mod_id, job_id, run_name):
        payload = {
            'username': user,
            'mod_id': = mod_id,
            'job_id': = job_id,
            'run_name': run_name
        }
        return self._pce_post("jobs", **payload)


    def check_connection(self, data=None):
        #
        # Ping the server to see if it is still available
        #
        s = requests.Session()
        url = "%s/cluster" % (self._url)
        r = s.get(url)

        self._logger.debug(self._name + "check_connection() " + str(r.status_code) + " from " + url)

        if r.status_code == 200:
            self._db.pce_update_state( self._pce_id, 0 ) # see onrampdb.py
            return True
        else:
            self._db.pce_update_state( self._pce_id, 2 ) # see onrampdb.py
            return False

    def establish_connection(self, data=None):
        #
        # Handshake to establish authorization (JJH TODO)
        #
        self._logger.debug(self._name + "establish_connection() Authorize - TODO")

        #
        # Check if it is a valid connection
        #
        is_connected = self.check_connection( data )
        if is_connected is False:
            return False

        #
        # Access the list of available modules
        #
        self._logger.debug(self._name + "establish_connection() Get available modules")
        s = requests.Session()
        url = "%s/modules/?state=Available" % (self._url)
        r = s.get(url)

        if r.status_code != 200:
            self._db.pce_update_state( self._pce_id, 2 ) # see onrampdb.py
            return False

        result = r.json()
        self._logger.debug(self._name + "\n" + json.dumps(r.json(), sort_keys=True, indent=4, separators=(',',': ')) )

        # Add to the modules table (if not already there)
        all_mods = {}
        module_id = 0
        for module in result['modules']:
            self._logger.debug(self._name + "establish) Add Module: " + module['mod_name'])
            mod_info = self._db.module_add_if_new(module['mod_name'])
            module_id = mod_info['id']
            all_mods[module['mod_name']] = module_id

            # Add it to the PCE/Module pair table (if not already there)
            self._logger.debug(self._name + "establish) Add Module to PCE: " + str(self._pce_id) + " module " + str(module_id) )
            pair_info = self._db.pce_add_module(self._pce_id, module_id, module['source_location']['type'], module['source_location']['path'])

            state = -1
            if module['state'] == "Available":
                state = 1
            self._db.pce_update_module_state(self._pce_id, module_id, 1) # see onrampdb.py

        return True
