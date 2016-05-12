##################################################
# Justin Ragatz
#
# Make file for the Pi Simulation exercise.
##################################################

CC = gcc
OMP = -fopenmp
CFLAGS = -Wall -O0 -g
PROGS = pi_omp pi_seq

all: $(PROGS)

pi_omp: pi_omp.c
	$(CC) $(OMP) $(CFLAGS) pi_omp.c -o pi_omp

pi_seq: pi_seq.c
	$(CC) $(CFLAGS) pi_seq.c -o pi_seq

clean:
	$(RM) $(PROGS) *.o