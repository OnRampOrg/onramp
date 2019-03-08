""" Module for making requests to a PCE

"""
from django.forms import model_to_dict
from ui.admin.models import pce, module, module_to_pce, job
from django.contrib.auth.models import User
import requests
import logging
import json
import os

JOB_STATES = {
    0 : "Unknown job id",
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

class PCEAccess(object):
    """Client-side interface to OnRamp PCE server.

    Methods:
        get_modules_avail: Return the list of modules that are available at the
            PCE but not currently installed.
        get_modules: Return the list of modules that are available at the PCE
            but not currently installed. (or a specific ID)
        add_module: Install given module on this PCE.
        deploy_module: Initiate module deployment actions.
        delete_module: Delete given module from PCE.
        get_jobs: Return the requested jobs.
        launch_job: Initiate job launch.
        delete_job: Delete given job from PCE.
        check_connection: Ping the server to see if it is still available.
        establish_connection: Handshake to establish authorization (JJH TODO).
    """

    def __init__(self, pce_id):
        """Initialize PCEAccess instance.

        Args:
            logger (logging.Logger): Logger for instance to use.
            pce_id (int): Id of PCE instance should provide interface to.
        """
        self._pce_id = pce_id

        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        self._cur_dir = os.getcwd()

        self._logger = self._get_logger(pce_id)

        self._tmp_dir = "/".join(self._cur_dir.split("/")[:-1])+"/tmp"
        self._pce_dir = os.path.join(self._tmp_dir, "pce", str(self._pce_id))
        self._pce_module_dir = os.path.join(self._pce_dir, "modules")
        self._pce_job_dir = os.path.join(self._pce_dir, "jobs")

        if not os.path.exists(self._pce_dir):
            os.makedirs(self._pce_dir)
        if not os.path.exists(self._pce_module_dir):
            os.makedirs(self._pce_module_dir)
        if not os.path.exists(self._pce_job_dir):
            os.makedirs(self._pce_job_dir)

        #get pce_info from database
        pce_info = self._get_pce_info()
        self._url = self._get_url(pce_info.ip_addr, pce_info.ip_port)
        self._port = pce_info.ip_port
        self._name = pce_info.pce_name

    def _get_url(self, host, port):
        if port:
            # if the port is not 0 we assume we need it to
            # connect
            return "http://{}:{}".format(host, port)
        else:
            # otherwise we just use the hostname
            return "http://{}".format(host)


    def _get_logger(self, pce_id):
        FORMAT = '%(asctime)-15s %(levelname)-3s %(module)s: %(message)s'
        # logfile = "/".join(self._cur_dir.split("/")[:-1])+"/log/pce_connect.log"
        logfile = "/home/nick/Desktop/onramp/server/webserver/logs/pce_connect.log"

        logging.basicConfig(filename=logfile, level=logging.DEBUG, format=FORMAT)
        return logging.getLogger("[PCEAccess: {}]".format(pce_id))

    def _get_pce_info(self):
        """ Gets information from the Database about the PCE

        :return:
        """
        # TODO handle exceptions
        row = pce.objects.get(pce_id=self._pce_id)
        return row

    def get_modules_avail(self):
        """Return the list of modules that are available at the PCE but not
        currently installed.

        Returns:
            List of JSON-formatted module objects. Returns 'None' on error.
        """
        self._logger.debug("get_modules_avail(self) endpoint hit")

        response = self._pce_get("modules", state="Available")
        if not response or "modules" not in response.keys():
            return None
        return response["modules"]

    def get_modules(self, module_id=None):
        """Return the requested modules.

        Args:
            id (int): Id of the requested module. 'None' to return all modules.

        Returns:
            JSON-formatted module object for given id, or if no id given, list
            of JSON-formatted module objects. Returns 'None' on error.
        """
        self._logger.debug("get_modules(self, module_id=None) endpoint hit")

        url = "modules"
        if module_id:
            url += "/%d" % module_id

        response = self._pce_get(url)
        if not response:
            return None

        if module_id:
            if "module" not in response.keys():
                return None
            return response["module"]

        if "modules" not in response.keys():
            return None
        return response["modules"]

    def add_module(self, module_id, module_name, mod_type, mod_path):
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
            'mod_id': module_id,
            'mod_name': module_name,
            'source_location': {
                'type': mod_type,
                'path': mod_path
            }
        }
        return self._pce_post("modules", **payload)

    def deploy_module(self, module_id):
        """Initiate module deployment actions.

        Args:
            id (int): Id of the installed module to deploy.

        Returns:
            'True' if deployment request was successfully processed, 'False'
            if not.
        """
        endpoint = "modules/%d" % module_id
        return self._pce_post(endpoint)

    def delete_module(self, module_id):
        """Delete given module from PCE.

        Args:
            id (int): Id of the module to delete.

        Returns:
            'True' if delete request was successfully processed, 'False'
            if not.
        """
        endpoint = "modules/%d" % module_id
        return self._pce_delete(endpoint)

    def get_jobs(self, module_id):
        """Return the requested jobs.

        Args:
            id (int): Id of the requested job. 'None' to return all jobs.

        Returns:
            JSON-formatted job object for given id, or if no id given, list
            of JSON-formatted job objects. Returns 'None' on error.
        """
        url = "jobs/%d" % module_id

        response = self._pce_get(url)

        if not response:
            return None
        if "job" not in response.keys():
            return None

        return response["job"]

    def launch_job(self, user, mod_id, job_id, run_name, cfg_params=None):
        """Initiate job launch.

        Args:
            user (str): Username of user launching job.
            mod_id (int): Id of the module to run.
            job_id (int): Id to be given to launched job on PCE.
            run_name (str): Human-readable identifier for job.
            cfg_params (dict): Dict containing attrs to be written to
                onramp_runparams.cfg

        Returns:
            'True' if launch request was successfully processed, 'False' if not.
        """
        payload = {
            'username': user,
            'mod_id': mod_id,
            'job_id': job_id,
            'run_name': run_name
        }
        if cfg_params:
            payload['cfg_params'] = cfg_params
        return self._pce_post("jobs", **payload)

    def delete_job(self, job_id):
        """Delete given job from PCE.

        Args:
            id (int): Id of the job to delete.

        Returns:
            'True' if delete request was successfully processed, 'False'
            if not.
        """
        endpoint = "jobs/%d" % job_id
        return self._pce_delete(endpoint)

    def ping(self):
        """Ping the given PCE.

        Returns:
            HTTP response code from PCE ping request.
        """
        endpoint = "cluster/ping"
        return self._pce_get(endpoint, raw=True).status_code

    def check_connection(self):
        """Ping the server to see if it still available. Record status in given
        DB.

        Returns:
            True if connected, False if not.
        """
        status_code = self.ping()

        self._logger.debug("%scheck_connection() %d from %s"
                           % (self._name, status_code, self._url))

        pce_row = pce.objects.get(pce_id=self._pce_id)
        if status_code == 200:
            pce_row.state = 0
            pce_row.save()
            return True
        else:
            pce_row.state = 2
            pce_row.save()
            return False

    def establish_connection(self):
        #
        # Handshake to establish authorization (JJH TODO)
        #
        self._logger.debug(self._name + "establish_connection() Authorize - TODO")

        #
        # Check if it is a valid connection
        #
        is_connected = self.check_connection()
        if is_connected is False:
            return False

        #
        # Access the list of available modules
        #
        return self._refresh_modules_in_db( ("%sestablish_connection()" % self._name), avail=True )

    def refresh_module_states(self, module_id=None):
        if module_id is None:
            prefix = ("%srefresh_module_states()" % self._name)
        else:
            prefix = ("%srefresh_module_states(%s)" % (self._name, str(module_id)))

        self._refresh_modules_in_db(prefix, module_id)

    def _refresh_modules_in_db(self, prefix, module_id=None, avail=False):
        if module_id is None:
            if avail is True:
                self._logger.debug("%s Get all available modules" % prefix)
                avail_mods = self.get_modules_avail()
            else:
                self._logger.debug("%s Get all modules" % prefix)
                avail_mods = self.get_modules()
        else:
            self._logger.debug("%s Get module info for %s" % (prefix, str(module_id)))
            # JJH the below does not work as expected, so intead grab the whole
            #     list and extract just the one we care about
            #avail_mods = self.get_modules( int(module_id) )
            module_id = int(module_id)
            all_mods = self.get_modules()
            avail_mods = None
            for m in all_mods:
                m_id = module.objects.get(module_name=m['mod_name']).module_id
                if m_id == module_id:
                    avail_mods = m
                    #self._logger.debug("%s TESTING (1): %s" % (prefix, str(avail_mods)))
                    # JJH confirm this is the proper behavior
                    avail_mods = self.get_modules( int(module_id) )
                    #self._logger.debug("%s TESTING (2): %s" % (prefix, str(avail_mods)))
                    self._logger.debug("%s Get module info for %s: Found (I)" % (prefix, str(module_id)))
                    break

            if avail_mods is None:
                self._logger.debug("%s Get module info for %s: Searching Available" % (prefix, str(module_id)))
                all_mods = self.get_modules_avail()
                avail_mods = None
                for m in all_mods:
                    m_id = module.objects.get(module_name=m['mod_name']).module_id
                    if m_id == module_id:
                        avail_mods = m
                        self._logger.debug("%s Get module info for %s: Found (A)" % (prefix, str(module_id)))
                        break


        if avail_mods is None:
            pce_row = pce.objects.get(pce_id=self._pce_id)
            pce_row.state = 2
            pce_row.save()
            return False


        if module_id is None:
            for mod in avail_mods:
                rtn = self._update_module_in_db(prefix, mod)
                if rtn is False:
                    return False
        else:
            return self._update_module_in_db(prefix, avail_mods)

        return True

    def _save_job_output(self, job_id, output):
        prefix = ("%ssave_job_output(%s)" % (self._name, str(job_id)))
        self._logger.debug("%s Save Job output..." % prefix)
        #self._logger.debug("%s Save Job output: %s" % (prefix, str(output)))

        if output is None:
            return True

        job_dir = os.path.join(self._pce_job_dir, str(job_id))

        if not os.path.exists(job_dir):
            os.makedirs(job_dir)

        # Write it out
        output_file = os.path.join(job_dir, "output.txt")
        with open(output_file, 'w') as f:
            f.write(output)

        return True

    def get_job_output(self, job_id):
        prefix = ("%sget_job_output(%s)" % (self._name, str(job_id)))
        self._logger.debug("%s load Job output: %s" % (prefix, str(job_id)))

        job_dir = os.path.join(self._pce_job_dir, str(job_id))

        if not os.path.exists(job_dir):
            return None

        abs_output_file = os.path.join(job_dir, "output.txt")

        return abs_output_file

    def read_job_output(self, job_id):
        """ Returns the contents of the output file for the job

        :param job_id:
        :return:
        """
        output = self.get_job_output(job_id)
        if not output:
            return ""
        with open(output, 'r') as f:
            return f.read()


    def _save_uioptions(self, module_id, module_options):
        prefix = ("%ssave_uioptions(%s)" % (self._name, str(module_id)))
        self._logger.debug("%s Updating UI Options: %s" % (prefix, str(module_options)))

        module_dir = os.path.join(self._pce_module_dir, str(module_id))

        if not os.path.exists(module_dir):
            os.makedirs(module_dir)

        # Write it out to a file
        uioptions_file = os.path.join(module_dir, "uioptions.json")
        with open(uioptions_file, 'w') as f:
            json.dump(module_options, f)

        return True

    def _save_metadata(self, module_id, module_metadata):
        prefix = ("%ssave_metadata(%s)" % (self._name, str(module_id)))
        self._logger.debug("%s Updating Metadata: %s" % (prefix, str(module_metadata)))

        module_dir = os.path.join(self._pce_module_dir, str(module_id))

        if not os.path.exists(module_dir):
            os.makedirs(module_dir)

        # Write it out to a file
        metadata_file = os.path.join(module_dir, "metadata.json")
        with open(metadata_file, 'w') as f:
            json.dump(module_metadata, f)
        return True

    def get_module_uioptions(self, module_id, fields_only=False):
        prefix = ("%sget_module_uioptions(%s)" % (self._name, str(module_id)))
        self._logger.debug("%s Loading UI Options for module %s" % (prefix, str(module_id)))

        module_dir = self._pce_module_dir + "/" + str(module_id) + "/"

        if not os.path.exists(module_dir):
            return None

        # Read the JSON from a file
        uioptions_file = module_dir + "uioptions.json"
        module_options = None
        with open(uioptions_file, 'r') as f:
            module_options = json.load(f)

        if fields_only is True:
            # JJH Assume only two levels deep
            options = {}
            for out in module_options:
                # self._logger.debug("%s Outer: %s" % (prefix, str(out)))
                options[out] = []
                for inner in module_options[out]:
                    # self._logger.debug("%s Outer: %s Inner: %s" % (prefix, str(out), str(inner)))
                    # options[out][inner] = ""
                    options[out].append(inner)
            return options

        return module_options

    def get_module_metadata(self, module_id, fields_only=False):
        """NOT FULLY FUNCTIONAL YET
        TODO: need to set up module to communicate necessary data and make sure file is written before trying to read it.
        """
        prefix = ("%sget_module_metadata(%s)" % (self._name, str(module_id)))
        self._logger.debug("%s Loading Metadata for module %s" % (prefix, str(module_id)))

        module_dir = os.path.join(self._pce_module_dir, str(module_id))

        if not os.path.exists(module_dir):
            return None

        # Read the JSON from a file
        metadata_file = os.path.join(module_dir, "metadata.json")
        if not os.path.exists(metadata_file):
            return None

        module_metadata = None
        with open(metadata_file, 'r') as f:
            module_metadata = json.load(f)

        if fields_only is True:
            # JJH Assume only two levels deep
            metadata = {}
            for out in module_metadata:
                # self._logger.debug("%s Outer: %s" % (prefix, str(out)))
                metadata[out] = []
                for inner in module_metadata[out]:
                    # self._logger.debug("%s Outer: %s Inner: %s" % (prefix, str(out), str(inner)))
                    # options[out][inner] = ""
                    metadata[out].append(inner)
            return metadata

        return module_metadata

    def _update_module_in_db(self, prefix, module_data):
        if module_data['state'] == "Does not exist":
            self._logger.error("%s Asking to update a module that does not exist. %s" % (prefix, str(module_data)))
            try:
                pm_pair = module_to_pce.objects.filter(module_id=module_data['mod_id'], pce_id=self._pce_id)
                pm_pair.state = 0
                pm_pair.save()
            except Exception:
                # This means the pair does not exist
                pass
            return False

        self._logger.debug("%s Add Module: %s" % (prefix, module_data['mod_name']))

        mod_info, created = module.objects.get_or_create(
                                module_name=module_data['mod_name'])
        module_id = int(mod_info.module_id)

        # Add it to the PCE/Module pair table (if not already there)
        self._logger.debug("---------------------------------------------------")
        self._logger.debug("%s Add Module to PCE: %d module %d"
                           % (prefix, self._pce_id, module_id))

        if 'uioptions' in module_data and module_data["uioptions"] is not None:
            self._save_uioptions(module_id, module_data["uioptions"])

        if 'metadata' in module_data and module_data["metadata"] is not None:
            self._save_metadata(module_id, module_data["metadata"])

        pm_row, created = module_to_pce.objects.get_or_create(
            pce_id=self._pce_id, module_id=module_id,
            defaults={
                "src_location_type": module_data['source_location']['type'],
                "src_location_path": module_data['source_location']['path']
            })

        self._logger.debug("%s Add Module to PCE: %d module %d : State = %s"
                           % (prefix, self._pce_id, module_id, str(module_data['state'])))
        state = -99
        if module_data['state'] == "Does not exist":
            state = 0
        elif module_data['state'] == "Available":
            state = 1
        elif module_data['state'] == "Checkout in progress":
            state = 2
        elif module_data['state'] == "Checkout failed":
            state = -2
        elif module_data['state'] == "Installed":
            state = 3
        elif module_data['state'] == "Deploy in progress":
            state = 4
        elif module_data['state'] == "Deploy failed":
            state = -4
        elif module_data['state'] == "Admin required":
            state = 5
        elif module_data['state'] == "Module ready":
            state = 6
        pm_row.state = state
        pm_row.save()

    def install_and_deploy_module(self, module_id):
        prefix = ("%sinstall_deploy()" % self._name)

        #
        # Make sure this ID is available on the PCE
        #
        if self._refresh_modules_in_db(prefix) is False:
            return {'error_msg': "Module with id %d does not exist on the PCE" % (module_id)}

        # Get module info from db
        module_info = module_to_pce.objects.get(pce_id=self._pce_id, module_id=module_id)
        self._logger.debug("%s Module state %d (%s)" % (prefix, module_info["state"], module_info["state_str"]))

        #
        # Install the module (if it is not already installed)
        #
        if module_info["state"] <= 1:
            rtn = self.add_module(module_info["module_id"], module_info["module_name"],
                                  module_info["src_location_type"], module_info["src_location_path"])
            if rtn is False:
                return {'error_msg': "Failed to install the module"}
            self._logger.debug("%s Module %d installed" % (prefix, module_id))
        else:
            self._logger.debug("%s Module %d already installed (state=%d)" % (prefix, module_id, module_info["state"]))

        #
        # Deploy the module (if it is not already deployed successfully)
        #
        if module_info["state"] not in [4, 5, 6]:
            rtn = self.deploy_module(int(module_id))
            if rtn is False:
                return {'error_msg': "Failed to deploy the module"}
            self._logger.debug("%s Module %d deployed" % (prefix, module_id))
        else:
            self._logger.debug(
                "%s Module %d already deploy(ing) (state=%d)" % (prefix, module_id, module_info["state"]))

        #
        # Update the DB
        #
        self._refresh_modules_in_db(prefix, module_id)
        # self._refresh_modules_in_db( prefix )

        # rdata = self._db.pce_add_module( pce_id, module_id )
        # if 'error_msg' in rdata.keys():
        #     self.logger.info(prefix + " " + rdata['error_msg'])
        #     raise cherrypy.HTTPError(400)

        return {}

    def _update_job_in_db(self, prefix, job_id):

        self._logger.debug("%s Checking on Job %d" % (prefix, job_id))
        job_info = self.get_jobs(job_id)

        # This is a temp fix (though after analysis may prove to be THE fix). #
        if 'job_id' not in job_info:
            job_info['job_id'] = job_id
        if 'output' not in job_info:
            job_info['output'] = None
        if 'state' not in job_info:
            job_info['state'] = 'Setting up launch'
        #######################################################################

        self._logger.debug("%s job RAW %s" % (prefix, str(job)))
        self._save_job_output(job_info["job_id"], job_info["output"])

        self._logger.debug("%s Response: ID = %d/%d, State = %s"
                           % (prefix, job_info["job_id"], job_id, job_info["state"]))
        state = -99
        if job_info['state'] == "Setting up launch":
            state = 1
        elif job_info['state'] == "Launch failed":
            state = -1
        elif job_info['state'] == "Preprocessing":
            state = 2
        elif job_info['state'] == "Preprocess failed":
            state = -2
        elif job_info['state'] == "Scheduled":
            state = 3
        elif job_info['state'] == "Schedule failed":
            state = -3
        elif job_info['state'] == "Queued":
            state = 4
        elif job_info['state'] == "Running":
            state = 5
        elif job_info['state'] == "Run failed":
            state = -5
        elif job_info['state'] == "Postprocessing":
            state = 6
        elif job_info['state'] == "Done":
            state = 7
        # Update the database
        job_row = job.objects.get(job_id=job_id)
        job_row.state = state
        job_row.save()

        return state

    def check_on_job(self, job_id):
        job_id = int(job_id)
        prefix = ("%scheck_on_job()" % self._name)

        # Pull update from PCE to the DB
        state_id = self._update_job_in_db(prefix, job_id)
        self._logger.debug(
            "%s Checking on the job... %d = %s" % (prefix, state_id, JOB_STATES.get(state_id)))

        # Get full info from DB to return
        job_obj = job.objects.get(job_id=job_id)
        job_info = model_to_dict(job_obj)
        job_info["state_str"] = JOB_STATES.get(job_info["state"])

        output = self.get_job_output(job_id)
        if output is None:
            output = ""

        job_info["output_file"] = output
        # save the row with the output file in the database
        job_obj.output_file = output
        job_obj.save()
        # JJH Do we want this to be 'unzip'ed?
        return job_info

    def launch_a_job(self, user_id, workspace_id, module_id, job_data):
        prefix = ("%slaunch_a_job()" % self._name)

        #
        # Make sure the IDs are valid
        #
        self._logger.debug(
            "%s Checking IDs (%d, %d, %d) with %s" % (prefix, user_id, workspace_id, module_id, str(job_data)))

        user_info = User.objects.get(id=user_id)

        #
        # Get a job id from the DB
        #
        self._logger.debug("%s Getting Job ID from DB..." % prefix)
        try:
            job_row, created = job.objects.get_or_create(
                user_id=user_id, workspace_id=workspace_id,
                pce_id=self._pce_id, module_id=module_id,
                job_name=job_data['name'])
        except Exception:
            return {'error_msg': "Failed to start_job - Bad ID (%s)" % (str(job_data))}

        exists = not created
        job_id = job_row.job_id
        run_name = job_data["name"]
        cfg_params = job_data["uioptions"]

        self._logger.debug("%s DEBUG: Job Info %s / %d" % (prefix, str(exists), job_id))
        self._logger.debug("%s CFG Params: %s" % (prefix, str(cfg_params)))

        #
        # Launch the job with this configuration
        #
        if exists is False:
            self._logger.debug("%s Launching job ID %d on PCE... [exists=%s]" % (prefix, job_id, str(exists)))
            result = self.launch_job(user_info.username, module_id, job_id, run_name, cfg_params)
            if result is False:
                return {'error_msg': "Failed to deploy the module"}

        else:
            self._logger.debug("%s -Not- Launching job ID %d on PCE... [exists=%s]" % (prefix, job_id, str(exists)))

        #
        # Update status in the DB
        #
        state_id = self._update_job_in_db(prefix, job_id)
        self._logger.debug(
            "%s Checking on the job... %d = %s" % (prefix, state_id, JOB_STATES.get(state_id)))

        #
        # Return to the user
        #
        return {'exists': exists, 'job_id': job_id, 'state': state_id,
                'state_str': JOB_STATES.get(state_id)}

    def _pce_get(self, endpoint, raw=False, **kwargs):
        """Execute GET request to PCE endpoint.

        Args:
            endpoint (str): API URL endpoint for request. Must not have leading
                or trailing slashes.
            raw (bool): If True, return raw response, else return JSON portion
                of response only.

        Kwargs:
            Key/val pairs in kwargs will become key/val pairs included as HTTP
            query paramaters in the request.

        Returns:
            JSON response object on success, 'None' on error.
        """
        s = requests.Session()
        url = "%s/%s/" % (self._url, endpoint)
        r = s.get(url, params=kwargs)

        if r.status_code != 200:
            self._logger.error('%s Error: %d from GET %s: %s'
                               % (self._name, r.status_code, url, r.text))
            return None
        else:
            if raw:
                return r
            return r.json()

    def _pce_post(self, endpoint, **kwargs):
        """Execute JSON-formatted POST request to PCE endpoint.

        Args:
            endpoint (str): API URL endpoint for request. Must not have leading
                or trailing slashes.
            raw (bool): If True, return raw response, else return JSON portion
                of response only.

        Kwargs:
            Key/val pairs in kwargs will be included as JSON key/val pairs in
            the request body.

        Returns:
            'True' if request was successfully processed by RXing PCE, 'False'
            if not.
        """
        s = requests.Session()
        url = "%s/%s/" % (self._url, endpoint)
        data = json.dumps(kwargs)
        headers = {"content-type": "application/json"}
        r = s.post(url, data=data, headers=headers)

        if r.status_code != 200:
            self._logger.error('%s Error: %d from POST %s: %s'
                               % (self._name, r.status_code, url, r.text))
            return False

        response = r.json()

        if ((not response) or ('status_code' not in response.keys())
            or (0 != response['status_code'])):
            return False

        return True

    def _pce_delete(self, endpoint):
        """Execute DELETE request to PCE endpoint.

        Args:
            endpoint (str): API URL endpoint for request. Must not have leading
                or trailing slashes.
        Returns:
            'True' if request was successfully processed by RXing PCE, 'False'
            if not.
        """
        s = requests.Session()
        url = "%s/%s/" % (self._url, endpoint)
        r = s.delete(url)

        if r.status_code != 200:
            self._logger.error('%s Error: %d from DELETE %s: %s'
                               % (self._name, r.status_code, url, r.text))
            return False
        else:
            response = r.json()
            if ((not response) or ('status_code' not in response.keys())
                or (0 != response['status_code'])):
                return False
            return True

