# DESCRIPTION: Makefile for FWC program
# AUTHOR: Jason Regina
# REVISION: 13 May 2016
#
# Code Prefix
PREFIX=FWC-

# Compilers and Flags
CC=g++
EXECUTABLES=$(PREFIX)serial

# Dependencies
OBJS=soil.cpp

all:
	make clean
	make $(EXECUTABLES)

serial:
	make $(PREFIX)serial

$(PREFIX)serial: $(PREFIX)serial.cpp
	$(CC) $(PREFIX)serial.cpp $(OBJS) -o $(PREFIX)serial

clean:
	rm -f $(EXECUTABLES) *.o moisture_profile.csv
