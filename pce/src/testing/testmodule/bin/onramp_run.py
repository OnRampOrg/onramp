from subprocess import call

call(['mpirun', '-np', '4', 'src/testmodule.c-mpi'])
