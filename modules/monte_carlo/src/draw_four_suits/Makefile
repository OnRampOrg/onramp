######################################
# Justin Ragatz
#
# Make file for the Drawing Four Cards
# of the Same Suit exercise.
######################################

CC = gcc
OMP = -fopenmp
CFLAGS = -Wall -O0 -g
PROGS =  draw_four_suits_omp draw_four_suits_seq

all: $(PROGS)

draw_four_suits_omp: draw_four_suits_omp.c draw_four_suits_omp.h
	$(CC) $(OMP) $(CFLAGS) draw_four_suits_omp.c -o draw_four_suits_omp

draw_four_suits_seq: draw_four_suits_seq.c draw_four_suits_seq.h
	$(CC) $(CFLAGS) draw_four_suits_seq.c -o draw_four_suits_seq

clean:
	$(RM) $(PROGS) *.o