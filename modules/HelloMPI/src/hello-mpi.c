/*
  * $Id: hello-mpi.c,v 1.6 2012/06/27 19:49:09 ibabic09 Exp $
  * This file is part of BCCD, an open-source live CD for computational science
  * education.
  * 
  * Copyright (C) 2010 Andrew Fitz Gibbon, Paul Gray, Kevin Hunter, Dave 
  *   Joiner, Sam Leeman-Munk, Tom Murphy, Charlie Peck, Skylar Thompson, 
  *   & Aaron Weeden
  * 
  * This program is free software: you can redistribute it and/or modify
  * it under the terms of the GNU General Public License as published by
  * the Free Software Foundation, either version 3 of the License, or
  * (at your option) any later version.
  * 
  * This program is distributed in the hope that it will be useful,
  * but WITHOUT ANY WARRANTY; without even the implied warranty of
  * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  * GNU General Public License for more details.
  * 
  * You should have received a copy of the GNU General Public License
  * along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#include <stdio.h>
#include <mpi.h>
#include <string.h>
#include <stdlib.h>

#ifdef STAT_KIT
#include "../StatKit/petakit/pkit.h"    // For PetaKit output
#endif

/* This program illustrates the simplest of MPI programs.  The program 
 * leverages   the 'six essential' MPI calls, and one additional call 
 * that determines the name of the host where the program is running.  
 * To compile this program, issue:
 *     mpicc -o hello_world_mpi hello_world_mpi.c
 * In order to run the program on the bccd:
 *    i. Make sure that each of the hosts have run "bccd-allowall"
 *   ii. Check that all of the hosts are available with 
 *             bccd-checkem <machine-file>
 *  iii. Make the binary available on all hosts in the collective with
 *             bccd-syncdir <directory where hello_world_mpi is> <machinefile>
 *   iv. Change directories to where your files were sync'd to.
 *    v. Run the program with:
 *  mpirun -np <number of tasks> -machinefile <machinefile> ./hello_world_mpi
 */

// Clean up and die, takes in MPI error number, rank and user string
void fatal(const int, const int);
 
/* Typically process 0 in the ranking is the server process */
#define SERVER_RANK 0

int main(int argc, char **argv) {

#ifdef STAT_KIT
         startTimer();
#endif

    int my_rank, world_size, destination, tag, source, length, mpiErr;
    char message[256], name[80];
    MPI_Status status;

    MPI_Init(&argc, &argv); /* note that argc and argv are passed by address */

    MPI_Comm_rank(MPI_COMM_WORLD,&my_rank);
    MPI_Comm_size(MPI_COMM_WORLD,&world_size);

	/* Client code */ 
    if (my_rank != SERVER_RANK) {
        printf("I am the client, with rank %d of %d\n", my_rank, (world_size-1));
		MPI_Get_processor_name(name,&length);
        sprintf(message,"Greetings from process %d, %s!",my_rank,name);
        destination = SERVER_RANK; tag = 2;
        mpiErr = MPI_Send(message,strlen(message)+1,MPI_CHAR,destination,tag,MPI_COMM_WORLD);
		if(mpiErr != MPI_SUCCESS) {
			fprintf(stderr,"Rank %d - MPI_Send to %d failed!\n",my_rank,destination);
			fatal(mpiErr,my_rank);
		}
    }
    
    /* Server code */ 
    else { 
        printf("I am the server, with rank %d of %d\n", my_rank, (world_size-1));
        tag = 2;
        for (source = 1; source < world_size ; source ++) {
            mpiErr = MPI_Recv(message,256,MPI_CHAR,source,tag,MPI_COMM_WORLD, &status);
			if(mpiErr != MPI_SUCCESS) {
				fprintf(stderr,"Rank %d - MPI_Recv from %d failed!\n",SERVER_RANK,source);
				fatal(mpiErr,my_rank);
			}
            fprintf(stderr, "%s\n", message);
        }
    }

    printf("Calling Finalize %d\n",my_rank);

    MPI_Finalize();

#ifdef STAT_KIT
        printStats("Hello World MPI",world_size,"mpi",1, "1", 0, 0);
#endif


	exit(EXIT_SUCCESS);
}

void fatal(const int mpiErr, const int rank) {
	int resultLen;
	char mpiErrStr[MPI_MAX_ERROR_STRING];
	MPI_Error_string(mpiErr,mpiErrStr,&resultLen);
	fprintf(stderr,"Rank %d - %s\n",rank,mpiErrStr);
	MPI_Abort(MPI_COMM_WORLD,EXIT_FAILURE);
	exit(EXIT_FAILURE);
}
