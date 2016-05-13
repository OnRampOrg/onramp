# $Id: Makefile,v 1.1 2012/05/01 20:56:33 charliep Exp $

CC = gcc
CFLAGS = -Wall -O0 -g
PROGS = parameters

default:
	/bin/bash ./hpl.build

parameters: parameters.c
	$(CC) $(CFLAGS) parameters.c -o parameters

clean:
	$(RM) $(PROGS) *.o