#
# Makefile for the MPI program
#
# J. Hursey
#

# Use the MPI wrapper compiler
CC=mpicc

CFLAGS=-Wall -g -O0

LDFLAGS=-lm

#
# List all of the binary programs you want to build here
# Separate each program with a single space
#
PROGS=ring

all: $(PROGS)

ring: ring.c
	$(CC) -o ring $(CFLAGS) ring.c

clean:
	$(RM) $(PROGS) *.o
