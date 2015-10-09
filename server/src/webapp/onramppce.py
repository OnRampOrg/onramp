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

    def _pce_get_modules_avail():
        s = requests.Session()

        url = "%s/modules/?state=Available" % (self._url)

        r = s.get(url)

        if r.status_code != 200:
            self._logger.error(self._name + " Error: " + str(r.status_code) + " from GET " + url + ": " + str(r.reason))
            return None
        else:
            return r.json()

    def _pce_get_modules(id=None):
        s = requests.Session()

        if id is None:
            url = "%s/modules" % (self._url)
        else:
            url = "%s/modules/%d" % (self._url, id)

        r = s.get(url)

        if r.status_code != 200:
            self._logger.error(self._name + " Error: " + str(r.status_code) + " from GET " + url + ": " + str(r.reason))
            return None
        else:
            return r.json()

    def _pce_add_module(id, module_name, mod_type, mod_path):
        s = requests.Session()

        url = "%s/modules" % (self._url)

        headers = {'content-type': 'application/json'}

        payload = {}
        payload['mod_id'] = id
        payload['mod_name'] = module_name
        payload['source_location'] = {}
        payload['source_location']['type'] = mod_type
        payload['source_location']['path'] = mod_path

        r = s.post(url, data=json.dumps(payload), headers=headers)

        if r.status_code != 200:
            self._logger.error(self._name + " Error: " + str(r.status_code) + " from POST " + url + ": " + str(r.reason))
            return None

        return r.json()

    def _pce_deploy_module(id):
        s = requests.Session()

        url = "%s/modules/%d" % (self._url, id)

        headers = {'content-type': 'application/json'}

        payload = {}

        r = s.post(url, data=json.dumps(payload), headers=headers)

        if r.status_code != 200:
            self._logger.error(self._name + " Error: " + str(r.status_code) + " from POST " + url + ": " + str(r.reason))
            return None

        return r.json()

    def _pce_get_cluster():
        s = requests.Session()
        url = "%s/cluster" % (self._url)
        r = s.get(url)

        if r.status_code != 200:
            self._logger.error(self._name + " Error: " + str(r.status_code) + " from GET " + url + ": " + str(r.reason))
            return None

        return r.json()

    def _pce_get_jobs(id=None):
        s = requests.Session()

        if id is None:
            url = "%s/jobs" % (self._url)
        else:
            url = "%s/jobs/%d" % (self._url, id)

        r = s.get(url)

        if r.status_code != 200:
            self._logger.error(self._name + " Error: " + str(r.status_code) + " from GET " + url + ": " + str(r.reason))
            return None

        return r.json()

    def _pce_launch_job(user, mod_id, job_id, run_name):
        s = requests.Session()

        url = "%s/jobs" % (self._url)

        headers = {'content-type': 'application/json'}

        payload = {}
        payload['username'] = user
        payload['mod_id']   = mod_id
        payload['job_id']   = job_id
        payload['run_name'] = run_name

        r = s.post(url, data=json.dumps(payload), headers=headers)

        if r.status_code != 200:
            self._logger.error(self._name + " Error: " + str(r.status_code) + " from POST " + url + ": " + str(r.reason))
            return None

        return r.json()


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
