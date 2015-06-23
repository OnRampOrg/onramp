import os
from subprocess import call

os.chdir('src')
call(['make', 'c-mpi'])
