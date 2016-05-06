/*
 * This program is the first of threes exercise in the OnRamp to
 * Parallel Computing - Monte Carlo Module. We will flip a coin,
 * simulated using rand_r(), many times and evaluate the randomness of
 * the results using a chi-squared test. This exercise is derived from
 * Libby Shoop's CS in Parallel Monte Carlo Module. 
 *
 * History:
 *  Dave Valentine (Slippery Rock University): Original C++ program
 *  Libby Shoop    (Macalester University)   : Adapted for CS in 
 *                                             Parallel Module
 *  Justin Ragatz  (UW-La Crosse)            : Adapted for OnRamp Module
 *                                             rewritten in C.
 */
#include "coin_flip_omp.h"


int main(int argc, char *argv[]) {
    unsigned long long num_flips = 0;
    unsigned long long num_heads = 0;
    unsigned long long num_tails = 0;
    int n_threads = 1;    
    int tid;
    unsigned long long trial_flips = FLIPS_PER_TRIAL;
    unsigned long long max_flips   = FLIPS_PER_TRIAL * (1LLU<<TRIALS);
    double start_time = -1;
    double end_time   = -1;

    // Get number of threads
    if (argc > 1) {
	n_threads = atoi(argv[1]);
	if (n_threads > 32) {
	    n_threads = 32;
	}
    }

    create_strings(); /* Malloc and initialize strings. */

    /* Print introduction. */
    printf("\n Settings:           \n"                   );
    printf("    Trials         : %llu\n", TRIALS         );
    printf("    Flips per trial: %llu\n", FLIPS_PER_TRIAL);
    printf("    Threads        : %d\n", n_threads        );
    printf("\n Begin Simulation... \n"                   );

    /* Print table heading. */
    printf("\n ----------------------------------------"
	   "----------------------------------------\n");
    printf(" | %15s | %15s | %15s | %11s | %8s |\n",
	   "Trials", "Heads", "Tails", "Chi Squared", "Time");
    printf(" ----------------------------------------"
	   "----------------------------------------\n");

    /* Run the simulation. */
    while (trial_flips <= max_flips) {  

	num_heads = 0;
	num_tails = 0;

	start_time = omp_get_wtime();

        #pragma omp parallel num_threads(n_threads) default(none) \
	private(num_flips, tid) shared(trial_flips, seeds) \
	reduction(+:num_heads, num_tails)
	{
	    tid = omp_get_thread_num();
	    seeds[tid] = abs( ( (time(NULL) * 181) * ( (tid - 83) * 359 ) )
			      % 104729 );

            #pragma omp for
	    for (num_flips = 0; num_flips < trial_flips; num_flips++) {
		if (rand_r(&seeds[tid]) % 2 == 0) {
		    num_heads++;
		} else {
		    num_tails++;
		}
	    }
	}
        end_time = omp_get_wtime();

	pretty_int(trial_flips, trial_string);
	pretty_int(num_heads  , heads_string);
	pretty_int(num_tails  , tails_string);

	printf(" | %15s | %15s | %15s | %11.2f | %8.2f |\n",
	       trial_string, heads_string, tails_string,
	       chi_squared(num_heads, num_tails),
	       (double)(end_time - start_time));

        trial_flips *= 2;
    }
    
    printf(" ----------------------------------------"
	   "----------------------------------------\n");

    clean_exit(0);

    return 0;
}


double chi_squared(unsigned long long heads, unsigned long long tails) {
    double sum = 0;              // chi square sum
    double tot = heads + tails;  // total flips
    double expected = 0.5 * tot; // expected heads (or tails)
    
    sum = ((heads - expected) * (heads - expected) / expected) + 
	  ((tails - expected) * (tails - expected) / expected);
    
    return sum;
}


int pretty_int(unsigned long long n, char* s) {
    int extra  = 0;
    int commas = 0;
    int count  = 0;
    int len = 0;
    int i;

    if (NULL == s) return -1;

    len = sprintf(s, "%llu", n);

    if ( len > STRING_LEN ) {
	printf("Buffer overflow, cannot print string.\n");
	s = NULL;
	return -1;
    }

    extra = strlen(s) % 3;
    commas = (strlen(s) - extra) / 3;

    if (0 == extra) commas--;

    s[strlen(s) + commas] = '\0';

    for (i = strlen(s) - 1; i > 0; i--) {
	count++;
	count = count % 3;
	if (0 == count) {
	    s[i + commas] = s[i];
	    commas--;
	    s[i + commas] = ',';
	} else {
	    s[i + commas] = s[i];
	}
    }

    return 0;
}


int create_strings() {
    int i;

    trial_string = (char*) malloc (sizeof(char) * STRING_LEN);

    if (NULL == trial_string) {
	fprintf(stderr, "Error: Malloc for trial_string failed.\n");
	clean_exit(-1);
    }

    heads_string = (char*) malloc (sizeof(char) * STRING_LEN);

    if (NULL == heads_string) {
	fprintf(stderr, "Error: Malloc for heads_string failed.\n");
	clean_exit(-1);
    }

    tails_string = (char*) malloc (sizeof(char) * STRING_LEN);

    if (NULL == tails_string) {
	fprintf(stderr, "Error: Malloc for tails_string failed.\n");
	clean_exit(-1);
    }

    for (i = 0; i < STRING_LEN - 1; i++) {
	trial_string[i] = ' ';
	heads_string[i] = ' ';
	tails_string[i] = ' ';
    }

    trial_string[STRING_LEN - 1] = '\0';
    heads_string[STRING_LEN - 1] = '\0';
    tails_string[STRING_LEN - 1] = '\0';

    return 0;
}


int clean_exit(int status) {

    free(trial_string);
    free(heads_string);
    free(tails_string);

    trial_string = NULL;
    heads_string = NULL;
    tails_string = NULL;

    if (status == 0) {
	printf("\n Normal termination.\n\n");
    } else {
	fprintf(stderr, "\n Terminated by error.\n\n");
	exit(EXIT_FAILURE);
    }

    return 0;
}
