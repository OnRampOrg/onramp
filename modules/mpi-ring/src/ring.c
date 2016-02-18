/*
 * MPI Ring program in C
 *
 * J. Hursey
 *
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h> // usleep
#include "mpi.h"

int main(int argc, char *argv[])
{
    int rank, size, next, prev;
    int message, tag = 999;
    int max_iters, sim_work;
    int i;

    /*
     * Start up MPI
     */
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
 
    /*
     * Calculate the rank of the next process in the ring.  Use the
     * modulus operator so that the last process "wraps around" to
     * rank zero.
     */
    next = (rank + 1) % size;
    prev = (rank + size - 1) % size;

    /*
     * Determine number of iterations, and simulated work from cmdline
     *  -i #ITERS
     *  -w WORK_IN_USEC
     */
    max_iters = 10;
    sim_work = 1000;
    // Note that some MPI implementation do not share command line arguments
    //      with all ranks, so have Rank 0 parse them then Bcast them out
    if (0 == rank) {
        for( i = 1; i < argc; ++i ) {
            if( 0 == strncmp("-i", argv[i], 2) ) {
                i += 1;
                if( i < argc ) {
                    max_iters = strtol(argv[i], NULL, 10);
                }
                else {
                    fprintf(stderr, "Error: -i requires an integer parameter\n");
                    MPI_Finalize();
                    return -1;
                }
            }
            else if( 0 == strncmp("-w", argv[i], 2) ) {
                i += 1;
                if( i < argc ) {
                    sim_work = strtol(argv[i], NULL, 10);
                }
                else {
                    fprintf(stderr, "Error: -w requires an integer parameter\n");
                    MPI_Finalize();
                    return -2;
                }
            }
        }
    }
    MPI_Bcast(&max_iters, 1, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Bcast(&sim_work,  1, MPI_INT, 0, MPI_COMM_WORLD);

    /*
     * If we are the "master" process (i.e., MPI_COMM_WORLD rank 0),
     * put the number of times to go around the ring in the
     * message.
     */
    if (0 == rank) {
        message = 0;

        printf("Process %2d of %2d) [<-- %2d, %2d, %2d -->] Start Ring!\n",
               rank, size, prev, rank, next);

        usleep(sim_work); // simulate some work

        MPI_Send(&message, 1, MPI_INT, next, tag, MPI_COMM_WORLD); 
    }

    /*
     * Pass the message around the ring.  The exit mechanism works as
     * follows: the message (a positive integer) is passed around the
     * ring.  Each time it passes rank 0, it is incremented.  When
     * each processes receives a message containing a max value, it
     * passes the message on to the next process and then quits.  By
     * passing the message first, every process gets the final message
     * and can quit normally.
     */
    while (1) {
        // Receive from my previous neighbor
        MPI_Recv(&message, 1, MPI_INT,
                 prev, tag, MPI_COMM_WORLD, 
                 MPI_STATUS_IGNORE);

        // Checkin during the first round - for debugging
        if( max_iters == message && 0 != rank ) {
            printf("Process %2d of %2d) [<-- %2d, %2d, %2d -->] Recv/Send Checking in!\n",
                   rank, size, prev, rank, next);

            usleep(sim_work); // simulate some work during checkin
        }

        // Each time rank 0 sees the marker increment it
        if (0 == rank) {
            ++message;
            printf("Process %2d of %2d) [<-- %2d, %2d, %2d -->] Increment value %3d of %3d\n",
                   rank, size, prev, rank, next, message, max_iters);

            usleep(sim_work); // simulate some work
        }

        // Send to my next neighbor
        MPI_Send(&message, 1, MPI_INT,
                 next, tag, MPI_COMM_WORLD);

        // If all done then cleanup
        if (max_iters <= message) {
            printf("Process %2d of %2d) [<-- %2d, %2d, %2d -->] Exiting\n",
                   rank, size, prev, rank, next);
            break;
        }
    }

    /*
     * The last process does one extra send to process 0, which needs
     * to be received before the program can exit
     */
    if (0 == rank) {
        MPI_Recv(&message, 1, MPI_INT, prev, tag, MPI_COMM_WORLD,
                 MPI_STATUS_IGNORE);
    }
    
    /*
     * All done
     */
    MPI_Finalize();

    return 0;
}
