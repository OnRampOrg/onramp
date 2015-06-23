"""Service classes encapsulating onramp REST server functionality under HTTP
methods.

Exports:
    Service: Upload, launch, and get status of parallel jobs.
    PrebuiltLaunch: Launch a prebuilt parallel job.
    Request: Get results from previously run parallel jobs.
    ClusterDetails: Cluster attrs, status, etc.
    UserSetup: Create new users.
    Login: Authenticate users.
"""

import glob
import logging
import os
import json
import hashlib
import shutil
from multiprocessing import Process
from subprocess import call

from Crypto import Random
from Crypto.Cipher import AES

from tools import admin_authenticate, authenticate, decrypt, encrypt, launch_job


def _required_attrs(*args):
    """Decorator to specify and verify receipt of required attrs in HTTP
    request.

    *args: List of required HTTP request attrs.

    @_required_attrs is only intended to be applied to HTTP method dispatchers
    (POST, PUT, etc.).

    Example:
        @_required_attrs('username', 'password')
        def POST(self, **kwargs):
            ...
    """
    def inner1(f):
        def inner2(self, **kwargs):
            keys = kwargs.keys()
            missing_attrs = filter(lambda x: x not in keys, args)
            if missing_attrs:
                retval = 'The following required form fields are missing: '
                retval += '%s' % str(missing_attrs)
                self._logger.error(retval)
                return retval
            else:
                return f(self, **kwargs)
        return inner2
    return inner1


class Service:
    """Provide access to mechanism for uploading and launching new jobs.

    Attrs:
        exposed (bool): If True, object is directly accessible via the Web.
        self.conf (ConfigObj): Application configuration object.

    Methods:
        POST: Uploads and launches a new job.
    """
    exposed = True

    def __init__(self, conf):
        """Instantiate and set self.conf."""
        self.conf = conf
        self._logger = logging.getLogger('onramp')

    def _setup(self, base_dir, projectName, processors, verbose, emailResults,
              dateStamps, emailName, **kwargs):
        """Creates and launches new job located at base_dir/projectName.

        Args:
            project_loc (str): Filesystem path for the reqesting user's dir.
            projectName (str): Name for this particular run of the project.
            processors: Number of processors to run the given project on.
            verbose (str): Pseudo-boolean val indicating whether or not output from
                the run should be generated in verbose mode. 'true', 'on', '1',
                't', 'y', and 'yes' all indicate verbose mode. All other values
                indicate not verbose.
            emailResults (str): Pseudo-boolean val indicating whether or not
                output from the run should be emailed. 'true', 'on', '1', 't',
                'y', and 'yes' will all set the project to be emailed. All other
                values will not. emailName is required with email is set.
            dateStamps (str): Pseudo-boolean val indicating whether or not output
                from the run should be datestamped. 'true', 'on', '1', 't', 'y', and
                'yes' all set the project output to be datestamped. All other values
                do not.
            emailName (str): Email address to send output to, if configured.
            **kwargs: Representations of files to be added to the project of the
                form:
                    kwargs['kwarg1'].filename: Name of the file.
                    kwargs['kwarg1'].content_type: MIME-type of the file.
                    kwargs['kwarg1'].file: The file.

        """
        self._logger.debug('Service._setup() called')
        project_dir = base_dir + '/' + projectName
        results_dir = project_dir + '/Results'

        self._logger.info('Making results directory: %s' % results_dir)
        call(['mkdir', '-p', results_dir])

        self._logger.info('Copying user-uploaded files')
        for f in kwargs.itervalues():
            filename = project_dir + '/' + f.filename
            self._logger.debug('Writing file: %s' % filename)
            datafile = open(filename, 'w')
            while True:
                data = f.file.read(8192)
                if not data:
                    break
                datafile.write(data)
            datafile.close()

        self._logger.info('Launching job: %s' % projectName)
        launch_job(project_dir, projectName, processors, verbose,
                   emailResults, dateStamps, emailName,
                   self.conf['cluster']['batch_scheduler'])

    def POST(self, username, password, projectName, processors, verbose,
             emailResults, dateStamps, emailName, **kwargs):
        """Authenticates user, forks, creates and launches new job located at
        base_dir/projectName.

        Args:
            username (str): Username of submitting user.
            password (str): Password of submitting user.
            projectName (str): Name for this particular run of the project.
            processors: Number of processors to run the given project on.
            verbose (str): Pseudo-boolean val indicating whether or not output from
                the run should be generated in verbose mode. 'true', 'on', '1',
                't', 'y', and 'yes' all indicate verbose mode. All other values
                indicate not verbose.
            emailResults (str): Pseudo-boolean val indicating whether or not
                output from the run should be emailed. 'true', 'on', '1', 't',
                'y', and 'yes' will all set the project to be emailed. All other
                values will not. emailName is required with email is set.
            dateStamps (str): Pseudo-boolean val indicating whether or not output
                from the run should be datestamped. 'true', 'on', '1', 't', 'y', and
                'yes' all set the project output to be datestamped. All other values
                do not.
            emailName (str): Email address to send output to, if configured.
            **kwargs: Representations of files to be added to the project of the
                form:
                    kwargs['kwarg1'].filename: Name of the file.
                    kwargs['kwarg1'].content_type: MIME-type of the file.
                    kwargs['kwarg1'].file: The file.

        Returns:
            str: Status of job launch.

        """
        self._logger.debug('Service.POST() called')
        path = os.path.dirname(os.path.abspath(__file__)) + '/../..'
        base_dir = path + '/users/' + username

        self._logger.debug('Authenticating user: %s' % username)
        auth_response = authenticate(base_dir, username, password);
        if auth_response is not None:
            self._logger.warning('Failed auth_response: %s' % auth_response)
            return auth_response

        p = Process(target=self._setup,
                    args=(base_dir, projectName, processors, verbose,
                          emailResults, dateStamps, emailName),
                    kwargs=kwargs)

        p.daemon = True
        self._logger.debug('Starting new process with target Service._setup()')
        p.start()
        # Join if we would like to wait for newJob to return.  We generally
        # don't want this as we are creating a new process.
        #p.join()

        self._logger.info('User %s launched job %s', (username, projectName))
        return ('Launched a new job with ' + username)


class PrebuiltLaunch:
    """Provide access to mechanism for launching default shipped jobs.

    Attrs:
        exposed (bool): If True, object is directly accessible via the Web.
        self.conf (ConfigObj): Application configuration object.

    Methods:
        POST: Launches a job.
    """
    exposed = True

    def __init__(self, conf):
        """Instantiate and set self.conf."""
        self.conf = conf
        self._logger = logging.getLogger('onramp')

    def _get_prebuilt_proj_dir(self, x):
        return {
            '0': 'HelloMPI',
            '1': 'AreaUnderCurve',
        }.get(x, 'Error')

    def _copy_tree(self, src, dst):
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                self._logger.debug('Copying tree %s to %s' % (s,d))
                shutil.copytree(s, d)
            else:
                self._logger.debug('Copying file %s to %s' % (s,d))
                shutil.copy2(s, d)

    @_required_attrs('username', 'password', 'projectNum', 'projectName',
                    'processors')
    def POST(self, **kwargs):
        """Authenticates user and launches a default shipped job.

        Kwargs:
        -- Required kwargs:
            username (str): Username of submitting user.
            password (str): Password of submitting user.
            projectNum: Project number.
                **FIXME: Update to use project_name
                instead.
            projectName (str): Name for this particular run of the project.
                **FIXME: Update to use run_name instead.
            processors: Number of processors to run the given project on.
                **FIXME: Should be num_tasks, as that's what's really needed.

        -- Optional kwargs (Required if email notifications desired)
            emailResults (str): Pseudo-boolean val indicating whether or not
                output from the run should be emailed. 'true', 'on', '1', 't',
                'y', and 'yes' will all set the project to be emailed. All other
                values will not. emailName is required with email is set.
            emailName (str): Email address to send output to, if configured.

        Returns:
            str: Status of job launch.
        """
        self._logger.debug('PrebuiltLaunch.POST() called')

        username = kwargs['username']
        password = kwargs['password']
        projectNum = kwargs['projectNum']
        projectName = kwargs['projectName']
        processors = kwargs['processors']

        path = os.path.dirname(os.path.abspath(__file__)) + '/../..'
        base_dir = path + '/users/' + username
        prebuilt_dir = path + '/modules'

        self._logger.debug('Authenticating user: %s' % username)
        auth_response = authenticate(base_dir, username, password);
        if auth_response is not None:
            self._logger.warning('Failed auth_response: %s' % auth_response)
            return auth_response

        project_dir = base_dir + '/' + projectName
        results_dir = project_dir + '/' + 'Results'

        self._logger.info('Making results directory: %s' % results_dir)
        call(['mkdir', '-p', results_dir])

        # FIXME: Update the following to use project_name instead of projectNum.
        if int(projectNum) >= 0:
            # Copy module to user's dir.
            prebuilt_proj_dir = self._get_prebuilt_proj_dir(projectNum)
            if prebuilt_proj_dir == 'Error':
                retval = 'Unable to find and launch the specified '
                retval += 'prebuilt project.'
                self._logger.error(retval)
                self._logger.error('Unfound project number: %d' % projectNum)
                return retval

            self._logger.info('Copying project files from %s to %s'
                              % (prebuilt_dir + '/' + prebuilt_proj_dir,
                                 project_dir))
            self._copy_tree(prebuilt_dir + '/' + prebuilt_proj_dir, project_dir)
        else:
            retval = 'Invalid projectNum value: %s' % projectNum
            self._logger.error(retval)
            return retval

        #TODO: Store kwargs to module/conf/yet-to-be-determined-filename.ini
        # right here.

        self._logger.info('Launching job: %s' % projectName)
        if ('emailResults' in kwargs.keys()
            and kwargs['emailResults'] == 'true'
            and 'emailName' in kwargs.keys()):
                launch_job(project_dir, projectName,
                           self.conf['cluster']['batch_scheduler'], processors,
                           email=kwargs['emailName'])
        else:
            launch_job(project_dir, projectName,
                       self.conf['cluster']['batch_scheduler'], processors)

        self._logger.info('User %s launched job %s', (username, projectName))
        return ('Launched a new job with ' + username)


class Request:
    """Provide access to mechanism for obtaining job status.

    Attrs:
        exposed (bool): If True, object is directly accessible via the Web.
        self.conf (ConfigObj): Application configuration object.

    Methods:
        POST: Return status of all jobs for user.
    """
    exposed = True

    def __init__(self, conf):
        """Instantiate and set self.conf."""
        self.conf = conf
        self._logger = logging.getLogger('onramp')

    def POST(self, username, password):
        """Authenticate user and return status of all jobs submitted by user.

        Args:
            username (str): Username of user.
            password (str): Password of user.

        Returns:
            str: JSON rep of job data on success, indication of error on
                failure.
        """
        self._logger.debug('Request.POST() called')
        path = os.path.dirname(os.path.abspath(__file__)) + '/../..'
        base_dir = path + '/users/' + username

        self._logger.debug('Authenticating user: %s' % username)
        auth_response = authenticate(base_dir, username, password);
        if auth_response is not None:
            self._logger.warning('Failed auth_response: %s' % auth_response)
            return auth_response

        data = {}

        for folder in os.listdir(base_dir):
            project_dir = base_dir + '/' + folder
            results_dir = project_dir + '/Results'

            if os.path.isdir(results_dir) is False:
                continue

            results = ''
            self._logger.debug('Changing CWD to: %s' % results_dir)
            os.chdir(results_dir)
            for filename in glob.glob('*.txt'):
                self._logger.debug('Opening file: %s' % filename)
                file = open(filename)
                while True:
                    read_data = file.read(8192)
                    if not read_data:
                        break
                    results += read_data

            if results != '':
                data[folder] = results

        if not data:
            self._logger.info('No results found for user %s' % username)
            return 'No results found for this user!'

        self._logger.info('Results found')
        json_data = json.dumps(data, sort_keys=True, ensure_ascii=False)
        self._logger.debug('Results: %s' % json_data)
        return json_data


class ClusterDetails:
    """Provide access to mechanism for obtaining cluster attrs/status.

    Attrs:
        exposed (bool): If True, object is directly accessible via the Web.
        self.conf (ConfigObj): Application configuration object.

    Methods:
        POST: Return attrs/status of cluster.
    """
    exposed = True

    def __init__(self, conf):
        """Instantiate and set self.conf."""
        self.conf = conf
        self._logger = logging.getLogger('onramp')

    def POST(self, username, password):
        """Authenticate user and return attrs/status of cluster.

        Args:
            username (str): Username of user.
            password (str): Password of user.

        Returns:
            str: JSON rep of cluster attrs/status on success, indication of
                error on failure.
        """
        self._logger.debug('ClusterDetails.POST() called')
        path = os.path.dirname(os.path.abspath(__file__)) + '/../..'
        base_dir = path + '/users/' + username

        self._logger.debug('Authenticating user: %s' % username)
        auth_response = authenticate(base_dir, username, password);
        if auth_response is not None:
            self._logger.warning('Failed auth_response: %s' % auth_response)
            return auth_response

        data = {}

        # Ganglia Command Line
        # Review http://www.msg.ucsf.edu/local/ganglia/ganglia_docs/usage.html

        data['nodeCount'] = 17
        data['cpuCount'] = 80

        if not data:
            self._logger.info('No cluster details available')
            return 'Failed to collect cluster details.'

        json_data = json.dumps(data, ensure_ascii=False)
        self._logger.info('Returning cluster details')
        self._logger.debug('Cluster details: %s' % json_data)
        return json_data


class UserSetup:
    """Provide access to mechanism for user administration.

    Attrs:
        exposed (bool): If True, object is directly accessible via the Web.
        self.conf (ConfigObj): Application configuration object.

    Methods:
        POST: Create new user.
    """
    exposed = True

    def __init__(self, conf):
        """Instantiate and set self.conf."""
        self.conf = conf
        self._logger = logging.getLogger('onramp')

    def POST(self, adminUsername, adminPassword, username, password, isAdmin):
        """Authenticate admin and create new user.

        Args:
            adminUsername (str): Username of admin.
            adminPassword (str): Password of admin.
            username (str): Username of new user.
            password (str): Password of new user.
            isAdmin (str): 'true' if new user is to be admin.

        Returns:
            str: Status of user creation.
        """
        self._logger.debug('UserSetup.POST() called')
        path = os.path.dirname(os.path.abspath(__file__)) + '/../..'
        admin_dir = path + '/users/' + adminUsername

        self._logger.debug('Authenticating admin user %s' % adminUsername)
        auth_response = admin_authenticate(admin_dir, adminUsername,
                                           adminPassword);
        if auth_response is not None:
            self._logger.debug('Failed admin auth_response: %s' % adminUsername)
            return auth_response

        base_dir = path + '/users/' + username

        # Return if user directory already exists.
        if os.path.isdir(base_dir):
            self._logger.info('User %s already exists' % username)
            return 'Specified user already exists.'

        self._logger.info('Creating new user %s' % username)
        self._logger.debug('Creating new user directory for %s at '
                           % (username, base_dir))
        try:
            call(['mkdir', '-p', base_dir])
        except:
            self._logger.exception('User creation failed for %s' % username)
            return 'User creation failed. Unable to create user directory.'

        # Password default is username if empty.
        if password == '':
            self._logger.info('Setting default password for user %s' % username)
            password = username

        content = json.dumps([username, isAdmin], ensure_ascii=False)
        key = hashlib.sha256(password).digest()
        encrypted = encrypt(content, key)
        decrypted = decrypt(encrypted, key)

        security_file = open(base_dir + '/security', 'w')
        security_file.write(encrypted)
        security_file.close()

        usertype = 'user'
        if isAdmin == 'true':
            usertype = 'admin'

        retval = 'User setup successful. Created a new ' + usertype + ' - '
        retval += username + '.'
        self._logger.info(retval)
        return retval


class Login:
    """Provide access to authentication mechanism.

    Attrs:
        exposed (bool): If True, object is directly accessible via the Web.
        self.conf (ConfigObj): Application configuration object.

    Methods:
        POST: Authenticate the user.
    """
    exposed = True

    def __init__(self, conf):
        """Instantiate and set self.conf."""
        self.conf = conf
        self._logger = logging.getLogger('onramp')

    def POST(self, username, password):
        """Authenticate admin and create new user.

        Args:
            username (str): Username of new user.
            password (str): Password of new user.

        Returns:
            str: 'Success' if user, 'Admin' if admin, else indication of error.
        """
        self._logger.debug('Login.POST() called')
        path = os.path.dirname(os.path.abspath(__file__)) + '/../..'
        base_dir = path + '/users/' + username

        self._logger.debug('Authenticating user %s' % username)
        auth_response = authenticate(base_dir, username, password);
        if auth_response is not None:
            self._logger.debug('Failed auth_response: %s' % username)
            return auth_response

        self._logger.debug('Authenticating admin user %s' % username)
        auth_response = admin_authenticate(base_dir, username, password);
        if auth_response is not None:
            self._logger.info('User %s logged in' % username)
            return 'Success'

        self._logger.info('Admin %s logged in' % username)
        return 'Admin'


def _check_required_attrs(*args, **kwargs):
    """Return list of args not in kwargs.keys()."""
    keys = kwargs.keys()
    return filter(lambda x: x not in keys, args)


if __name__ == '__main__':
    p = PrebuiltLaunch()
    print p.POST('admin', 'admin', '0', 'hello-mpi', '4', 'false', 'testname',
             'false', 'false', None)
