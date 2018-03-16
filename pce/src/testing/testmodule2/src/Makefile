#
# Generic Makefile for the sample MPI program
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
PROGS=hello

all: $(PROGS)

hello: hello.c
	$(CC) -o hello $(CFLAGS) hello.c

clean:
	$(RM) $(PROGS) *.o
