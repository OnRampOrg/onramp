__doc__ = """
OnRamp job launching support package.
Provides functionality for launching jobs, as well as means of
setting/storing/updating job state data.
Exports:
    JobState: Encapsulation of job state that avoids race conditions.
    launch_job: Schedules job launch using system batch scheduler as configured
        in onramp_pce_config.cfg.
    get_jobs: Returns list of tracked jobs or single job.
    init_job_delete: Initiate the deletion of a job.
"""

from redis import StrictRedis
from subprocess import *
import logging
import shutil
import json
import time
import os

ret_dir = None
_job_state_dir = None
ConfigObj = None
Validator = None
Scheduler = None
module_log = None
pce_root = ""


class RedisState(object):
    def __init__(self, state_id, redis):
        self.id = state_id
        self.redis = redis
        self.state = None
        self.states = None
        self.r_states = None

    def _load_state(self):
        job_info = self.redis.get("job-{}".format(self.id))
        if job_info is not None:
            self.update(json.loads(job_info))

    def _save_state(self):
        job_info = {k: v for k, v in self.__dict__.iteritems()}
        # need to remove all of the attributes on the
        # class that cannot be represented as a string
        job_info.pop("redis", None)
        job_info.pop("states", None)
        job_info.pop("r_states", None)
        # put the state information into the redis db
        self.redis.set("job-{}".format(self.id), json.dumps(job_info))

    def __enter__(self):
        """Provide entry for use in 'with' statements."""
        # load the job from the redis database
        self._load_state()
        return self

    def __exit__(self, e_type, e_value, e_traceback):
        """Provide exit for use in 'with' statements."""
        # save the job to the redis database
        self._save_state()
        if e_type:
            return False

    def set(self, state):
        if state in self.r_states:
            self.state = self.r_states[state]
        else:
            raise ValueError("An invalid state was passed "
                             "to the {} class!".format(self.__name__))

    def update(self, data):
        # loop over the kwargs and update the class
        for k, v in data.iteritems():
            try:
                if getattr(self, k) is not None:
                    setattr(self, k, v)
            except AttributeError:
                # this shouldn't ever happen however if it did
                # it is because something was set on the class
                # that wasn't explicitly set in the __init__
                setattr(self, k, v)

    def clear(self):
        # clear all of the attributes on the class
        exempt_fields = ['id', 'redis', 'states', 'r_states']
        for k, v in self.__dict__.iteritems():
            if k not in exempt_fields:
                setattr(self, k, None)
        # save the state of the class into redis
        self._save_state()

    def delete(self):
        self.redis.delete("job-{}".format(self.id))


class ModState(RedisState):
    def __init__(self, mod_id, redis):
        super(ModState, self).__init__(mod_id, redis)
        self.state = None
        self.mod_name = None
        self.installed_path = None


class JobState(RedisState):
    def __init__(self, job_id, redis):
        super(JobState, self).__init__(job_id, redis)
        # setup defaults values for the class
        self.mod_id = None
        self.username = None
        self.run_name = None
        self.run_params = None
        self.run_dir = None
        self.scheduler_job_num = None
        self.state = None
        self.error = None
        self.mod_status_output = None
        self.output = None
        self.visible_files = None
        self.mod_name = None
        self.marked_for_del = False
        # set the valid states for the class
        self.states = {
            -1: "Launch failed",
            -2: "Preprocess failed",
            -3: "Schedule failed",
            -5: "Run failed",
            -99: "Error: Undefined",
            0: "Unknown job id",
            1: "Setting up launch",
            2: "Preprocessing",
            3: "Scheduled",
            4: "Queued",
            5: "Running",
            6: "Postprocessing",
            7: "Done"
        }
        self.r_states = {v: k for k, v in self.states.iteritems()}


class JobHandler(object):
    def __init__(self):
        self._log = logging.getLogger("onramp")
        self._mod_install_dir = os.path.join(pce_root, 'modules')
        self.rc0 = StrictRedis(db=0)  # Connection to JobState database
        self.rc1 = StrictRedis(db=1)  # Connection to ModState database

    def create(self, job_id, mod_id, username, run_name, run_params, run_dir=None):
        """

        :param job_id:
        :param mod_id:
        :param username:
        :param run_name:
        :param run_params:
        :param mod_state_file:
        :param run_dir:
        :return:
        """

        self._log.debug('Want JobState (init) at: %s' % time.time())

        with JobState(job_id, self.rc0) as job_state:
            job_state.update({
                'mod_id': mod_id,
                'username': username,
                'run_name': run_name,
                'run_params': run_params
            })
            self._log.debug('Initializing job at %s' % time.time())
            self._log.debug('PID: %d' % os.getpid())
            self._log.debug('Waiting on ModState at: %s' % time.time())
            with ModState(mod_id, self.rc1) as mod_state:
                self._log.debug('Done waiting on ModState at: %s' % time.time())
                if mod_state.state is None or mod_state.state != 'Module ready':
                    msg = 'Module not ready'
                    job_state.set('Launch failed')
                    job_state.error = msg
                    self._log.warn(msg)
                    self._log.warn('mod_state: %s' % str(mod_state))
                    if job_state.marked_for_del:
                        self.delete(job_state)
                        return -2, 'Job %d deleted' % job_id
                    return -1, 'Module not ready'
                job_state.mode_name = mod_state.mod_name
                proj_loc = mod_state.installed_path
                mod_name = mod_state.mod_name
                self._log.debug('Leaving modstate part of init')
            self._log.debug('Job state: %s' % str(job_state))
        self._log.debug('Done with JobState (init) at: %s' % time.time())

        self._log.debug('Testing project location')
        if not os.path.isdir(proj_loc):
            msg = 'Project location does not exist!'
            self._log.error(msg)
            return -1, msg
        self._log.debug('Project location exists!')

        # Initialize dir structure.
        if run_dir is None:
            user_dir = os.path.join(os.path.join(pce_root, 'users'), username)
            user_mod_dir = os.path.join(user_dir, '{}_{}'.format(mod_name, mod_id))
            run_dir = os.path.join(user_mod_dir, run_name)
            try:
                os.mkdir(user_dir)
            # Thrown if dir already exists.
            except OSError:
                pass
            try:
                os.mkdir(user_mod_dir)
            # Thrown if dir already exists.
            except OSError:
                pass

        self._log.debug('Setting run dir')
        with JobState(job_id, self.rc0) as job_state:
            job_state.run_dir = run_dir
            self._log.debug('state vals: %s' % job_state)
        self._log.debug('Run dir set')

        # The way the following is setup, if a run_dir has already been setup with
        # this run_name, it will be used (that is, not overwritten) for this launch.
        try:
            shutil.copytree(proj_loc, run_dir)
        except (shutil.Error, OSError):
            pass

        if run_params:
            self._log.debug('Handling run_params')
            spec = os.path.join(run_dir, 'config/onramp_uioptions.cfgspec')
            params = ConfigObj(run_params, configspec=spec)
            result = params.validate(Validator())
            if result:
                with open(os.path.join(run_dir, 'onramp_runparams.cfg'), 'w') as f:
                    params.write(f)
            else:
                msg = 'Runparams failed validation'
                self._log.warn(msg)
                return -1, msg

        return 0, 'Job state initialized'

    def pre_process(self, job_id):
        """

        :param job_id:
        :return:
        """

        ret_dir = os.getcwd()

        self._log.info('Calling bin/onramp_preprocess.py')
        self._log.debug('Want JobState (preprocess) at: %s' % time.time())

        with JobState(job_id, self.rc0) as job_state:
            self._log.debug('In JobState (preprocess) at: %s' % time.time())
            self._log.debug('preprocess PID: %d' % os.getpid())
            job_state.set('Preprocessing')
            job_state.error = None
            run_dir = job_state.run_dir

        os.chdir(run_dir)
        self._log.debug('Done with JobState (preprocess) at: %s' % time.time())

        try:
            path = os.path.join(pce_root, 'src/env/bin/python')
            command = [path, 'bin/onramp_preprocess.py']
            result = check_output(command, stderr=STDOUT)
        except CalledProcessError as e:
            code = e.returncode
            if code > 127:
                code -= 256
            result = e.output
            msg = 'Preprocess exited with return status %d and output: %s' % (code, result)
            self._log.error(msg)
            with JobState(job_id, self.rc0) as job_state:
                job_state.set('Preprocess failed')
                job_state.error = msg
                if job_state.marked_for_del:
                    self.delete(job_state)
                    return -2, 'Job %d deleted' % job_id
            return -1, msg
        finally:
            module_log(run_dir, 'preprocess', result)
            os.chdir(ret_dir)

        return 0, 'Job preprocess complete'

    def run(self, job_id):
        """

        :param job_id:
        :return:
        """

        # Determine batch scheduler to user from config.
        cfg = ConfigObj(os.path.join(pce_root, 'bin', 'onramp_pce_config.cfg'),
                        configspec=os.path.join(pce_root, 'src', 'configspecs',
                                                'onramp_pce_config.cfgspec'))
        cfg.validate(Validator())
        scheduler = Scheduler(cfg['cluster']['batch_scheduler'])

        self._log.debug("in job_run: trying to launch using scheduler %s", cfg['cluster']['batch_scheduler'])
        # ret_dir = os.getcwd() # FIXME: determine if this is supposed to be commented out or not
        with JobState(job_id, self.rc0) as job_state:
            run_dir = job_state.run_dir
            run_name = job_state.run_name

        os.chdir(run_dir)

        # self._log.debug("in job_run: attempting to be in %s, really in %s", run_dir, os.get_cwd())
        # Load run params:
        run_np = None
        run_nodes = None
        run_cfg = ConfigObj('onramp_runparams.cfg')
        if 'onramp' in run_cfg.keys():
            if 'np' in run_cfg['onramp']:
                run_np = run_cfg['onramp']['np']
            if 'nodes' in run_cfg['onramp']:
                run_nodes = run_cfg['onramp']['nodes']

        self._log.debug("in job_run: loaded params np: %d and nodes: %d", run_np, run_nodes)
        # Write batch script.
        with open('script.sh', 'w') as f:
            if run_np and run_nodes:
                f.write(scheduler.get_batch_script(run_name, numtasks=run_np, num_nodes=run_nodes))
            elif run_np:
                f.write(scheduler.get_batch_script(run_name, numtasks=run_np))
            elif run_nodes:
                f.write(scheduler.get_batch_script(run_name, num_nodes=run_nodes))
            else:
                f.write(scheduler.get_batch_script(run_name))

        # Schedule job.
        result = scheduler.schedule(run_dir)
        if result['status_code'] != 0:
            self._log.error(result['msg'])
            with JobState(job_id, self.rc0) as job_state:
                job_state.set('Schedule failed')
                job_state.error = result['msg']
                os.chdir(ret_dir)
                if job_state.marked_for_del:
                    self.delete(job_state)
                    return -2, 'Job %d deleted' % job_id
            return result['returncode'], result['msg']

        with JobState(job_id, self.rc0) as job_state:
            job_state.set('Scheduled')
            job_state.error = None
            job_state.scheduler_job_num = result['job_num']
            os.chdir(ret_dir)
            if job_state.marked_for_del:
                self.delete(job_state)
                return -2, 'Job %d deleted' % job_id

        return 0, 'Job scheduled'

    def post_process(self, job_id):
        """

        :param job_id:
        :return:
        """

        self._log.info('PCE.tools.jobs._job_postprocess() called')

        # Get attrs needed.
        with JobState(job_id, self.rc0) as job_state:
            username = job_state.username
            mod_id = job_state.mod_id
            run_name = job_state.run_name
            mod_name = job_state.mod_name
            run_dir = job_state.run_dir

        args = (username, mod_name, mod_id, run_name)
        ret_dir = os.getcwd()

        os.chdir(run_dir)
        self._log.debug('Calling bin/onramp_postprocess.py')
        try:
            path = os.path.join(pce_root, 'src/env/bin/python')
            command = [path, 'bin/onramp_postprocess.py']
            result = check_output(command, stderr=STDOUT)

        except CalledProcessError as e:
            code = e.returncode
            if code > 127:
                code -= 256
            result = e.output
            msg = 'Postprocess exited with return status %d and output: %s' % (code, result)
            with JobState(job_id, self.rc0) as job_state:
                job_state.set('Postprocess failed')
                job_state.error = msg
                self._log.error(msg)

                os.chdir(ret_dir)

                if job_state.marked_for_del:
                    self.delete(job_state)
                    return -2, 'Job %d deleted' % job_id
            return -1, msg

        finally:
            module_log(run_dir, 'postprocess', result)

        # Grab job output.
        with open('output.txt', 'r') as f:
            output = f.read()

        os.chdir(ret_dir)

        # Update state.
        with JobState(job_id, self.rc0) as job_state:
            job_state.set('Done')
            job_state.error = None
            job_state.output = output
            if job_state.marked_for_del:
                self.delete(job_state)
                return -2, 'Job %d deleted' % job_id

    def delete(self, job_id):
        """

        :param job_id:
        :return:
        """
        job_cancel_states = ['Scheduled', 'Queued', 'Running']
        finished_states = ['Launch failed', 'Schedule failed', 'Preprocess failed',
                           'Run failed', 'Postprocess failed', 'Done']
        finished_states += job_cancel_states

        with JobState(job_id, self.rc0) as job_state:
            if job_state.state is None:
                return -1, 'Job %d does not exist' % job_id
            if job_state.state in finished_states:
                job_cancel_states = ['Scheduled', 'Queued', 'Running']
                if job_state.state in job_cancel_states:
                    cfgfile = os.path.join(pce_root, 'bin', 'onramp_pce_config.cfg')
                    specfile = os.path.join(pce_root, 'src', 'configspecs',
                                            'onramp_pce_config.cfgspec')
                    cfg = ConfigObj(cfgfile, configspec=specfile)
                    cfg.validate(Validator())
                    scheduler = Scheduler(cfg['cluster']['batch_scheduler'])
                    result = scheduler.cancel_job(job_state.scheduler_job_num)
                    self._log.debug('Cancel job output: %s' % result[1])
                args = (job_state.username, job_state.mode_name, job_state.mod_id,
                        job_state.run_name)
                run_dir = os.path.join(pce_root, 'users/%s/%s_%d/%s' % args)
                shutil.rmtree(run_dir, ignore_errors=True)
                job_state.clear()
                return 0, 'Job %d deleted' % job_id
            job_state.marked_for_del = True
            return 0, 'Job %d marked for deletion' % job_id

    def launch(self, job_id, mod_id, username, run_name, run_params):
        """
        :param job_id:
        :param mod_id:
        :param username:
        :param run_name:
        :param run_params:
        :return:
        """

        # Initialize job state.
        self._log.debug('JobHandler.launch() called')
        self._log.debug('Checking if state exists and if so is accepted')

        # check to see if the job has already been launched or failed
        failed_states = ['Schedule failed', 'Launch failed', 'Preprocess failed']
        with JobState(job_id, self.rc0) as job_state:
            if job_state.state is not None and job_state.state not in failed_states:
                msg = 'Job launch already initiated. Current state {}.'.format(job_state.state)
                self._log.warn(msg)
                return -1, msg

        # attempt to create the job and make sure it ran successfully
        ret = self.create(job_id, mod_id, username, run_name, run_params)
        if ret[0] != 0:
            return ret

        # call the pre process method for the job if it exists
        ret = self.pre_process(job_id)
        if ret[0] != 0:
            return ret

        # call the run method of the job to start running it
        return self.run(job_id)

    def get_state(self):
        """

        :return:
        """
        pass

    def get_states(self):
        """

        :return:
        """
        pass


if __name__ == '__main__':
    r = JobState(0, StrictRedis(db=0))
    with r as state:
        r.set("Run failed")
        r.error = "adfasdfas"
        r.test = "Test"
    r.delete()
