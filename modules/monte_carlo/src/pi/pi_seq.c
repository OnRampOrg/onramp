/*
 * Sequential version of a program to compute pi using Monte Carlo Methods.
 *
 * Justin Ragatz 
 */
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main (int argc, char *argv[]) {
    int i;      // For loop
    int hits;   // How many times we "hit" in the zone
    int trials; // How many iterations to run
    unsigned int seed;
    double x, y;
    clock_t start, end;

    if (argc > 1) {
	trials = atoi(argv[1]);
    } else {
	printf("Usage ./pi_seq <number of trials>\n");
	return -1;
    }

    printf("Trials : %7d\n", trials);

    start  = clock();
    hits   = 0;
    seed = (unsigned int) time(NULL);
    srand(seed);

    for (i = 0; i < trials; i++) {
	x = (double)rand_r(&seed) / RAND_MAX;
	y = (double)rand_r(&seed) / RAND_MAX;
	if (x*x + y*y <= 1.0) {
	    hits++;
	}
    }

    end = clock();

    printf("Time   : %7.2fs\n\n", (double)(end - start) / (double)CLOCKS_PER_SEC);
    printf("Estimate of pi: %7.5f\n", 4.0 * hits / trials);

    return 0;
}
