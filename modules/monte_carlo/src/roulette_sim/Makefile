##################################################
# Justin Ragatz
#
# Make file for the Routlette Simulation exercise.
##################################################

CC = gcc
OMP = -fopenmp
CFLAGS = -Wall -O0 -g
PROGS = roulette_sim_omp roulette_sim_seq

all: $(PROGS)

roulette_sim_omp: roulette_sim_omp.c roulette_sim_omp.h
	$(CC) $(OMP) $(CFLAGS) roulette_sim_omp.c -o roulette_sim_omp

roulette_sim_seq: roulette_sim_seq.c roulette_sim_seq.h
	$(CC) $(CFLAGS) roulette_sim_seq.c -o roulette_sim_seq

clean:
	$(RM) $(PROGS) *.o