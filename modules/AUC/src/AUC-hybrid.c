// Program: AUC-hybrid
// Author: Jason Regina
// Date: 12 November 2015
// Description: This program approximates pi using the Riemann Sum method

#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <math.h>
#include <mpi.h>
#include <omp.h>

// This function returns a y-value on a unit circle 
// centered at the origin, given an x-value
double func(double x)
{
    return sqrt(1.0 - (x * x));
}

int main( int argc, char** argv )
{
    // Set number of rectangles
    int recs = 100000000;
    int num_threads = 1;

    // Initialize MPI
    int rank = 0, procs = 0;
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &procs);

    // Parse command line
    const char* name = argv[0];
    int c;

    while ((c = getopt(argc, argv, "n:t:")) != -1)
    {
        switch(c)
        {
            case 'n':
                recs = atoi(optarg);
                break;
            case 't':
                num_threads = atoi(optarg);
                break;
            case '?':
            default:
                fprintf(stderr, "Usage: %s -n [NUMBER_OF_RECTANGLES] -t [NUM_OMP_THREADS]\n", name);
                return -1;
        }
    }
    argc -+ optind;
    argv += optind;

    // Calculate rectangle width
    double width;
    width = 1.0 / recs;

    // Determine first and last elements of process
    int first = 0, last = recs;
    first = rank * (recs / procs);
    if (rank != (procs - 1))
        last = first + (recs / procs);

    // Set number of OMP_THREADS
    omp_set_num_threads(num_threads);

    // Calculate total area
    double sum = 0.0;
    int i = 0;

#pragma omp parallel for reduction(+:sum) shared(first,last,width) private(i)
    for (i = first; i < last; i++)
    {
        sum += func(width * i) * width * 4.0;
    }

    // Calculate total sum
    double total_sum = 0.0;
    MPI_Reduce(&sum, &total_sum, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);

    // Print result
    if (rank == 0)
    {
	printf(" --- %s --- \n", name);
	printf("Number of processes: %d\n", procs);
	printf("Threads per process: %d\n", num_threads);
        printf("Rectangles         : %d\n", recs);
        printf("pi is approximately: %f\n", total_sum);
    }

    // Terminate
    MPI_Finalize();
    return 0;
}
