// Program: AUC-openmp
// Author: Jason Regina
// Date: 12 November 2015
// Description: This program approximates pi using the Riemann Sum method

#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <math.h>
#include <omp.h>

// This function returns a y-value on a unit circle 
// centered at the origin, given an x-value
double func(double x)
{
    return sqrt(1.0 - (x * x));
}

int main( int argc, char** argv )
{
    // Set number of rectangles and OMP threads
    int recs = 100000000;
    int num_threads = 1;

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
                fprintf(stderr, "Usage: %s -n [NUMBER_OF_RECTANGLES] -t [OMP_NUM_THREADS]\n", name);
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

    // Calculate total area
    double sum = 0.0;
    int i = 0;

    // Set OMP Threads
    omp_set_num_threads(num_threads);

#pragma omp parallel for reduction(+:sum) shared(first,last,width) private(i)
    for (i = first; i < last; i++)
    {
        sum += func(width * i) * width * 4.0;
    }

    // Print result
    printf(" --- %s --- \n", name);
    printf("Number of processes: %d\n", 1);
    printf("Threads per process: %d\n", num_threads);
    printf("Rectangles         : %d\n", recs);
    printf("pi is approximately: %f\n", sum);

    // Terminate
    return 0;
}
