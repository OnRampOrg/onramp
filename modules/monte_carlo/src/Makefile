######################################################
# Justin Ragatz
#
# Make file for the Coin-flipping in Parllel exercise.
######################################################

CC = gcc
OMP = -fopenmp
CFLAGS = -Wall -O0 -g
PROGS = coin_flip_omp coin_flip_seq draw_four_suits_omp draw_four_suits_seq roulette_sim_omp roulette_sim_seq

all: $(PROGS)

coin_flip_omp: coin_flip/coin_flip_omp.c coin_flip/coin_flip_omp.h
	$(CC) $(OMP) $(CFLAGS) coin_flip/coin_flip_omp.c -o coin_flip_omp

coin_flip_seq: coin_flip/coin_flip_seq.c coin_flip/coin_flip_seq.h
	$(CC) $(CFLAGS) coin_flip/coin_flip_seq.c -o coin_flip_seq

draw_four_suits_omp: draw_four_suits/draw_four_suits_omp.c draw_four_suits/draw_four_suits_omp.h
	$(CC) $(OMP) $(CFLAGS) draw_four_suits/draw_four_suits_omp.c -o draw_four_suits_omp

draw_four_suits_seq: draw_four_suits/draw_four_suits_seq.c draw_four_suits/draw_four_suits_seq.h
	$(CC) $(CFLAGS) draw_four_suits/draw_four_suits_seq.c -o draw_four_suits_seq

roulette_sim_omp: roulette_sim/roulette_sim_omp.c roulette_sim/roulette_sim_omp.h
	$(CC) $(OMP) $(CFLAGS) roulette_sim/roulette_sim_omp.c -o roulette_sim_omp

roulette_sim_seq: roulette_sim/roulette_sim_seq.c roulette_sim/roulette_sim_seq.h
	$(CC) $(CFLAGS) roulette_sim/roulette_sim_seq.c -o roulette_sim_seq

clean:
	$(RM) $(PROGS) *.o