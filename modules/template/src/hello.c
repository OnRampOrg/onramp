/*
 * Sample MPI "hello world" application in C
 *
 * J. Hursey
 *
 */

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "mpi.h"

int main(int argc, char* argv[])
{
    int rank, size, len;
    char processor[MPI_MAX_PROCESSOR_NAME];
    char *name = NULL;

    /*
     * Initialize the MPI library
     */
    MPI_Init(&argc, &argv);

    /*
     * Check to see if we have a command line argument for the name
     */
    if( argc > 1 ) {
        name = strdup(argv[1]);
    }
    else {
        name = strdup("World");
    }

    /*
     * Get my 'rank' (unique ID)
     */
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

    /*
     * Get the size of the world (How many other 'processes' are there)
     */
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    /*
     * Get the processor name (usually the hostname)
     */
    MPI_Get_processor_name(processor, &len);

    /*
     * Print a message from this process
     */
    printf("Hello, %s! I am %2d of %d on %s!\n", name, rank, size, processor);

    /*
     * Shutdown the MPI library before exiting
     */
    MPI_Finalize();

    /*
     * Cleanup
     */
    if( NULL != name ) {
        free(name);
        name = NULL;
    }

    return 0;
}
