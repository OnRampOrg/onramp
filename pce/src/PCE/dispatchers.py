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

import copy
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
        def inner2(self, *fargs, **kwargs):
            keys = kwargs.keys()
            missing_attrs = filter(lambda x: x not in keys, args)
            if missing_attrs:
                retval = 'The following required form fields are missing: '
                retval += ', '.join(missing_attrs)
                self._logger.error(retval)
                return retval
            return f(self, *fargs, **kwargs)
        return inner2
    return inner1


def _auth_required(f):
    """Decorator to perform authentication prior to execution of decorated
    function.

    Args:
        f (func): Function requiring an authenticated user.

    NOTE: Raises KeyError if 'username' or 'password' are missing from kwargs.
    """
    def inner(self, *args, **kwargs):
        path = os.path.dirname(os.path.abspath(__file__)) + '/../..'
        base_dir = path + '/users/' + kwargs['username']
        self._logger.debug('Authenticating user: %s' % kwargs['username'])
        auth_response = authenticate(base_dir, kwargs['username'],
                                     kwargs['password'])
        if auth_response:
            self._logger.warning('Failed auth_response: %s' % auth_response)
            return auth_response

        return f(self, *args, **kwargs)
    return inner


def _admin_auth_required(f):
    """Decorator to perform authentication of admin user prior to execution of
    decorated function.

    Args:
        f (func): Function requiring an authenticated admin user.

    NOTE: Raises KeyError if 'username' or 'password' are missing from kwargs.
    """
    def inner(self, *args, **kwargs):
        path = os.path.dirname(os.path.abspath(__file__)) + '/../..'
        base_dir = path + '/users/' + kwargs['adminUsername']
        self._logger.debug('Authenticating admin user: %s'
                           % kwargs['adminUsername'])
        auth_response = admin_authenticate(base_dir, kwargs['adminUsername'],
                                           kwargs['adminPassword'])
        if auth_response:
            self._logger.warning('Failed admin auth_response: %s'
                                 % auth_response)
            return auth_response

        return f(self, *args, **kwargs)
    return inner


def _santitize_dict(d):
    """Return copy of d with specified keys deleted.

    Args:
        d (dict): Dictionary to make a sanitized copy of.

    Returns:
        dict: Copy of d with specified keys deleted.
    """
    keys_to_del = ['password', 'files']

    new = copy.deepcopy(d)
    for k in filter(lambda x: x in d.keys(), keys_to_del):
        new.pop(k)
    return new


class Service:
    """Provide access to mechanism for uploading and launching new jobs.

    Attrs:
        exposed (bool): If True, object is directly accessible via the Web.
        self.conf (ConfigObj): Application configuration object.

    Methods:
        POST: Uploads and launches a new job.
    """
    exposed = True
    POST_required_attrs = ['username', 'password', 'projectNum', 'projectName',
                           'processors', 'files']

    def __init__(self, conf):
        """Instantiate and set self.conf."""
        self.conf = conf
        self._logger = logging.getLogger('onramp')

    @_required_attrs(*POST_required_attrs)
    @_auth_required
    def _setup(self, base_dir, **kwargs):
        """Creates and launches new job located at base_dir/projectName.

        Args:
            base_dir (str): Filesystem path for the reqesting user's dir.

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
            files: Dict of files to be uploaded into the new project. Format:
                files['key1'].filename: Name of file.
                files['key1'].content_type: MIME-type of file.
                files['key1'].file: The file.

        -- Optional kwargs (Required if email notifications desired)
            emailResults (str): Pseudo-boolean val indicating whether or not
                output from the run should be emailed. 'true', 'on', '1', 't',
                'y', and 'yes' will all set the project to be emailed. All other
                values will not. emailName is required with email is set.
            emailName (str): Email address to send output to, if configured.
        """
        username = kwargs['username']
        password = kwargs['password']
        projectNum = kwargs['projectNum']
        projectName = kwargs['projectName']
        processors = kwargs['processors']
        files = kwargs['files']

        self._logger.debug('Service._setup() called')
        project_dir = base_dir + '/' + projectName
        results_dir = project_dir + '/Results'

        self._logger.info('Making results directory: %s' % results_dir)
        call(['mkdir', '-p', results_dir])

        self._logger.info('Copying user-uploaded files')
        for f in files.itervalues():
            filename = project_dir + '/' + f.filename
            self._logger.debug('Writing file: %s' % filename)
            datafile = open(filename, 'w')
            while True:
                data = f.file.read(8192)
                if not data:
                    break
                datafile.write(data)
            datafile.close()

        #TODO: Store _sanitize_dict(kwargs) to
        # module/conf/to-be-determined-filename.ini right here.

        self._logger.info('Launching job: %s' % projectName)
        if('emailResults' in kwargs.keys()
           and kwargs['emailResults'] == 'true'
           and 'emailName' in kwargs.keys()):
                launch_job(project_dir, projectName,
                           self.conf['cluster']['batch_scheduler'], processors,
                           email=kwargs['emailName'])
        else:
            launch_job(project_dir, projectName,
                       self.conf['cluster']['batch_scheduler'], processors)

    @_required_attrs(*POST_required_attrs)
    @_auth_required
    def POST(self, **kwargs):
        """Authenticates user, forks, creates and launches new job located at
        base_dir/projectName.

        **FIXME: REQUIRES UPDATE OF WEB CLIENT!!!
            - **kwargs previously contained files for upload from user. Now
              file dict needs to be passed under the 'files' attr.

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
            files: Dict of files to be uploaded into the new project.

        -- Optional kwargs (Required if email notifications desired)
            emailResults (str): Pseudo-boolean val indicating whether or not
                output from the run should be emailed. 'true', 'on', '1', 't',
                'y', and 'yes' will all set the project to be emailed. All other
                values will not. emailName is required with email is set.
            emailName (str): Email address to send output to, if configured.

        Returns:
            str: Status of job launch.

        """
        username = kwargs['username']
        projectName = kwargs['projectName']

        self._logger.debug('Service.POST() called')
        path = os.path.dirname(os.path.abspath(__file__)) + '/../..'
        base_dir = path + '/users/' + username

        p = Process(target=self._setup, args=(base_dir,),
                    kwargs=_sanitize_dict(kwargs))
        p.daemon = True
        self._logger.debug('Starting new process with target Service._setup()')
        p.start()

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
    POST_required_attrs = ['username', 'password', 'projectNum', 'projectName',
                           'processors']

    def __init__(self, conf):
        """Instantiate and set self.conf."""
        self.conf = conf
        self._logger = logging.getLogger('onramp')

    def _get_prebuilt_proj_dir(self, x):
        # FIXME: This has to go. We should do this my project name instead.
        return {
            '0': 'HelloMPI',
            '1': 'AreaUnderCurve',
            '2': 'testmodule',
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

    @_required_attrs(*POST_required_attrs)
    @_auth_required
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
        self._logger.debug('kwargs: %s' % str(kwargs))

        username = kwargs['username']
        password = kwargs['password']
        projectNum = kwargs['projectNum']
        projectName = kwargs['projectName']
        processors = kwargs['processors']

        path = os.path.dirname(os.path.abspath(__file__)) + '/../..'
        base_dir = path + '/users/' + username
        prebuilt_dir = path + '/modules'

        project_dir = base_dir + '/' + projectName
        results_dir = project_dir + '/' + 'Results'

        if os.path.isdir(project_dir):
            retval = 'A job with this name already exists.'
            self._logger.info(retval)
            return retval

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

        #TODO: Store _sanitize_dict(kwargs) to
        # module/conf/to-be-determined-filename.ini right here.

        self._logger.info('Launching job: %s' % projectName)
        if('emailResults' in kwargs.keys()
           and kwargs['emailResults'] == 'true'
           and 'emailName' in kwargs.keys()):
                launch_job(project_dir, projectName,
                           self.conf['cluster']['batch_scheduler'],
                           num_tasks=processors, email=kwargs['emailName'])
        else:
            launch_job(project_dir, projectName,
                       self.conf['cluster']['batch_scheduler'],
                       num_tasks=processors)

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

    @_auth_required
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

        data = {}
        ret_dir = os.getcwd()

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

        self._logger.debug('Changing CWD to: %s' % ret_dir)
        os.chdir(ret_dir)

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

    @_auth_required
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

    @_admin_auth_required
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
        base_dir = path + '/users/' + username

        self._logger.debug('Authenticating admin user %s' % adminUsername)

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
