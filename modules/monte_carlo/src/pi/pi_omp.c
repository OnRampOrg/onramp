/*
 * OpenMP version of program to estimate pi using Monte Carlo Methods.
 *
 * Justin Ragatz
 */
#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
#include <time.h>

int main (int argc, char *argv[]) {
    int i;      // For loop
    int hits;   // How many times we "hit" the zone
    int trials; // Number of trials to run
    int n_threads;
    int seed;
    double x, y;
    double start, end;
    struct drand48_data buffer;

    if (argc > 2) {
	trials    = atoi(argv[1]);
	n_threads = atoi(argv[2]);
    } else {
	printf("Usage: ./pi_omp <trials> <threads>\n");
	return -1;
    }

    omp_set_num_threads (n_threads);

    printf("Trials  : %7d\n", trials);
    printf("Threads : %7d\n", n_threads);

    start = omp_get_wtime();
    hits = 0;

#pragma omp parallel private(i, x, y, seed, buffer) shared(trials)
    {
	seed = 1202107158 + omp_get_thread_num() * time(NULL);
	srand48_r (seed, &buffer);

#pragma omp for reduction(+:hits)
	for (i = 0; i < trials; i++) {
	    drand48_r (&buffer, &x);
	    drand48_r (&buffer, &y);
	    if (x*x + y*y <= 1.0) {
		hits++;
	    }
	}
    }

    end = omp_get_wtime();
    printf("Time    : %7.2fs\n\n", end - start);
    printf("Estimate of pi: %7.5f\n", 4.0 * hits / trials);

    return 0;
}
