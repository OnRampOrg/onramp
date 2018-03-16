// Program: AUC-serial
// Author: Jason Regina
// Date: 12 November 2015
// Description: This program approximates pi using the Riemann Sum method

#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <math.h>

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

    // Parse command line
    const char* name = argv[0];
    int c;

    while ((c = getopt(argc, argv, "n:")) != -1)
    {
        switch(c)
        {
            case 'n':
                recs = atoi(optarg);
                break;
            case '?':
            default:
                fprintf(stderr, "Usage: %s -n [NUMBER_OF_RECTANGLES]\n", name);
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
    for (i = first; i != last; ++i)
    {
        sum += func(width * i) * width * 4.0;
    }

    // Print result
    printf(" --- %s --- \n", name);
    printf("Number of processes: %d\n", 1);
    printf("Threads per process: %d\n", 1);
    printf("Rectangles         : %d\n", recs);
    printf("pi is approximately: %f\n", sum);

    // Terminate
    return 0;
}
