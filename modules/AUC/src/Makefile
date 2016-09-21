# DESCRIPTION: Makefile for AUC program
# AUTHOR: Jason Regina
# REVISION: 12 November 2015
#
# Code Prefix
PREFIX=AUC-

# Compilers and Flags
CC=gcc
MPICC=mpicc
LDFLAGS=-lm
EXECUTABLES=$(PREFIX){serial,mpi,openmp,hybrid}

all:
	make clean
	make $(EXECUTABLES)

serial:
	make $(PREFIX)serial

mpi:
	make $(PREFIX)mpi

openmp:
	make $(PREFIX)openmp

hybrid:
	make $(PREFIX)hybrid

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

