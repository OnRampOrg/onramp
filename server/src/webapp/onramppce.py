"""Functionality to support interacting with an OnRamp PCE

Exports:
    PCEAccess: Client-side interface to OnRamp PCE server.
"""
import os
import json
import requests

class PCEAccess():
    """Client-side interface to OnRamp PCE server.

    Methods:
        get_modules_avail: Return the list of modules that are available at the
            PCE but not currently installed.
        get_modules: Return the list of modules that are available at the PCE
            but not currently installed.
        add_module: Install given module on this PCE.
        deploy_module: Initiate module deployment actions.
        get_jobs: Return the requested jobs.
        launch_job: Initiate job launch.
        check_connection: Ping the server to see if it is still available.
        establish_connection: Handshake to establish authorization (JJH TODO).
    """
    _name = "[PCEAccess] "

    def __init__(self, logger, dbaccess, pce_id):
        """Initialize PCEAccess instance.

        Args:
            logger (logging.Logger): Logger for instance to use.
            dbaccess (onrampdb.DBAccess): Interface to server DB.
            pce_id (int): Id of PCE instance should provide interface to. Must
                exist in DB provided by dbaccess.
        """
        self._logger = logger
        self._db     = dbaccess
        self._pce_id = pce_id

        #
        # Get the PCE server information
        #
        pce_info = self._db.pce_get_info(pce_id)
        self._url = "http://%s:%d" % (pce_info['data'][2], pce_info['data'][3])

    def _pce_get(endpoint, **kwargs):
        """Execute GET requests to PCE endpoints.

        Args:
            endpoint (str): API URL endpoint for request. Must not have leading
                or trailing slashes.

        Kwargs:
            Key/val pairs in kwargs will become key/val pairs included as HTTP
            query paramaters in the request.

        Returns:
            JSON response object on success, 'None' on error.
        """
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
        """Execute JSON-formatted POST requests to PCE endpoints.

        Args:
            endpoint (str): API URL endpoint for request. Must not have leading
                or trailing slashes.

        Kwargs:
            Key/val pairs in kwargs will be included as JSON key/val pairs in
            the request body.

        Returns:
            'True' if request was successfully processed by RXing PCE, 'False'
            if not.
        """
        s = requests.Session()
        url = "%s/%s" % (self._url, endpoint)
        data = json.dumps(kwargs)
        headers = {"content-type": "application/json"}
        r = s.post(url, data=data, headers=headers)

        if r.status_code != 200:
            self._logger.error(self._name + " Error: " + str(r.status_code)
                               + " from GET " + url + ": " + str(r.status_msg))
            return False
        else:
            response = r.json()
            if ((not response) or ('status_code' not in response.keys())
                or (0 != response['status_code'])):
                return False
            return True

    def get_modules_avail():
        """Return the list of modules that are available at the PCE but not
        currently installed.

        Returns:
            List of JSON-formatted module objects. Returns 'None' on error.
        """
        response = self._rce_get("modules", state="Available")
        if (not response) or ("modules" not in response.keys()):
            return None
        return [mod for mod in response["modules"]]

    def get_modules(id=None):
        """Return the requested modules.

        Args:
            id (int): Id of the requested module. 'None' to return all modules.

        Returns:
            JSON-formatted module object for given id, or if no id given, list
            of JSON-formatted module objects. Returns 'None' on error.
        """
        s = requests.Session()
        url = "modules"
        if id:
            url += "/%d" % id

        response = self._pce_get(url)
        if not resposne:
            return None

        if id:
            if "module" not in response.keys():
                return None
            return response["module"]

        if "modules" not in response.keys():
            return None
        return [mod for mod in response["modules"]]
            

    def add_module(id, module_name, mod_type, mod_path):
        """Install given module on this PCE.

        Args:
            id (int): Id to be given to installed module on PCE.
            module_name (str): Name to be given to installed module on PCE.
            mod_type (str): Type of module source. Currently supported options:
                'local'.
            mod_path (str): Path, formatted as required by given mod_type, of
                the installation source.

        Returns:
            'True' if installation request was successfully processed, 'False'
            if not.
        """
        payload = {
            'mod_id': id,
            'mod_name': module_name,
            'source_location': {
                'type': mod_type,
                'path': mod_path
            }
        }
        return self._pce_post("modules", **payload)

    def deploy_module(id):
        """Initiate module deployment actions.

        Args:
            id (int): Id of the installed module to deploy.

        Returns:
            'True' if deployment request was successfully processed, 'False'
            if not.
        """
        endpoint = "modules/%d" % id
        return self._pce_post(endpoint)

    def get_jobs(id=None):
        """Return the requested jobs.

        Args:
            id (int): Id of the requested job. 'None' to return all jobs.

        Returns:
            JSON-formatted job object for given id, or if no id given, list
            of JSON-formatted job objects. Returns 'None' on error.
        """
        s = requests.Session()
        url = "jobs"
        if id:
            url += "/%d" % id

        response = self._pce_get(url)
        if not resposne:
            return None

        if id:
            if "job" not in response.keys():
                return None
            return response["job"]

        if "jobs" not in response.keys():
            return None
        return [job for job in response["jobs"]]


    def launch_job(user, mod_id, job_id, run_name):
        """Initiate job launch.

        Args:
            user (str): Username of user launching job.
            mod_id (int): Id of the module to run.
            job_id (int): Id to be given to launched job on PCE.
            run_name (str): Human-readable identifier for job.

        Returns:
            'True' if launch request was successfully processed, 'False' if not.
        """
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
