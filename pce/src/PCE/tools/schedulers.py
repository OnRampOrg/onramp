import os
from subprocess import CalledProcessError, check_output, STDOUT

class BatchScheduler(object):
    def __init__(self, type):
        self.type = type

class SLURMScheduler(BatchScheduler):
    @classmethod
    def is_scheduler_for(cls, type):
        return type == 'SLURM'

    def get_batch_script(self, run_name, numtasks=4, email=None,
                         filename='script.sh'):
        contents = '#!/bin/bash\n'
        contents += '\n'
        contents += '###################################\n'
        contents += '# Slurm Submission options\n'
        contents += '#\n'
        contents += '#SBATCH --job-name=' + run_name + '\n'
        contents += '#SBATCH -o output.txt\n'
        contents += '#SBATCH -n ' + str(numtasks) + '\n'
        if email:
            logger.debug('%s configured for email reporting to %s'
                         % (run_name, email))
            contents += '#SBATCH --mail-user=' + email + '\n'
        contents += '###################################\n'
        contents += '\n'
        contents += 'python bin/onramp_run.py\n'
        return contents
        
    def schedule(self, proj_loc):
        ret_dir = os.getcwd()
        os.chdir(proj_loc)
        try:
            batch_output = check_output(['sbatch', 'script.sh'], stderr=STDOUT)
        except CalledProcessError as e:
            msg = 'Job scheduling call failed'
            os.chdir(ret_dir)
            return {
                'returncode': e.returncode,
                'msg': '%s: %s' % (msg, e.output)
            }
        os.chdir(ret_dir)
        output_fields = batch_output.strip().split()

        if 'Submitted batch job' != ' '.join(output_fields[:-1]):
            msg = 'Unexpeted output from sbatch'
            self.logger.error(msg)
            return {
                'status_code': -7,
                'status_msg': msg
            }

        try:
            job_num = int(output_fields[3:][0])
        except ValueError, IndexError:
            msg = 'Unexpeted output from sbatch'
            self.logger.error(msg)
            return {
                'status_code': -7,
                'status_msg': msg
            }

        return {
            'status_code': 0,
            'status_msg': 'Job %d scheduled' % job_num,
            'job_num': job_num
        }

class SGEScheduler(BatchScheduler):
    @classmethod
    def is_scheduler_for(cls, type):
        return type == 'SGE'

def Scheduler(type):
  for cls in BatchScheduler.__subclasses__():
      if cls.is_scheduler_for(type):
            return cls(type)
      raise ValueError
