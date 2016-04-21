######################################################
# Justin Ragatz
#
# Make file for the Coin-flipping in Parllel exercise.
######################################################

CC = gcc
OMP = -fopenmp
CFLAGS = -Wall -O0 -g
PROGS = coin_flip_omp coin_flip_seq

all: $(PROGS)

coin_flip_omp: coin_flip_omp.c coin_flip_omp.h
	$(CC) $(OMP) $(CFLAGS) coin_flip_omp.c -o coin_flip_omp

coin_flip_seq: coin_flip_seq.c coin_flip_seq.h
	$(CC) $(CFLAGS) coin_flip_seq.c -o coin_flip_seq

clean:
	$(RM) $(PROGS) *.o