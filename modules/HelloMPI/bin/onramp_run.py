from subprocess import call

call(['mpirun', '-np', '4', 'src/hello-mpi.c-mpi'])
