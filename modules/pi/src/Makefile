# DESCRIPTION: Makefile for pi program
# AUTHOR: Jason Regina
# REVISION: 5 July 2015
#
# Code Prefix
PREFIX=pi-

# Compilers and Flags
CC=gcc
MPICC=mpicc
LDFLAGS=-lm
EXECUTABLES=$(PREFIX){serial,mpi,openmp,hybrid}

$(PREFIX)serial: $(PREFIX)serial.c
	$(CC) $(PREFIX)serial.c $(LDFLAGS) -o $(PREFIX)serial

$(PREFIX)mpi: $(PREFIX)mpi.c
	$(MPICC) $(PREFIX)mpi.c $(LDFLAGS) -o $(PREFIX)mpi

$(PREFIX)openmp: $(PREFIX)openmp.c
	$(CC) $(PREFIX)openmp.c -fopenmp $(LDFLAGS) -o $(PREFIX)openmp

$(PREFIX)hybrid: $(PREFIX)hybrid.c
	$(MPICC) $(PREFIX)hybrid.c -fopenmp $(LDFLAGS) -o $(PREFIX)hybrid

clean:
	rm -f $(EXECUTABLES) *.o

serial:
	make $(PREFIX)serial

mpi:
	make $(PREFIX)mpi

openmp:
	make $(PREFIX)openmp

hybrid:
	make $(PREFIX)hybrid

all:
	make clean
	make $(EXECUTABLES)

