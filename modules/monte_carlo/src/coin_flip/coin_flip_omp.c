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
    int num_flips = 0;
    int num_heads = 0;
    int num_tails = 0;
    int tid;
    unsigned int trial_flips = FLIPS_PER_TRIAL;
    unsigned int max_flips   = FLIPS_PER_TRIAL * (1<<TRIALS);
    double start_time = -1;
    double end_time   = -1;

    create_strings(); /* Malloc and initialize strings. */

    /* Print introduction. */
    printf("\n Settings:           \n"                 );
    printf("    Trials         : %d\n", TRIALS         );
    printf("    Flips per trial: %d\n", FLIPS_PER_TRIAL);
    printf("\n Begin Simulation... \n"                 );

    /* Print table heading. */
    printf("\n -----------------------------------"
	   "------------------------------------\n");
    printf(" | %12s | %12s | %12s | %11s | %8s |\n",
	   "Trials", "Heads", "Tails", "Chi Squared", "Time");
    printf(" -----------------------------------"
	   "------------------------------------\n");

    /* Run the simulation. */
    while (trial_flips <= max_flips) {  

	num_heads = 0;
	num_tails = 0;

	start_time = omp_get_wtime();

        #pragma omp parallel num_threads(N_THREADS) default(none) \
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

	printf(" | %12s | %12s | %12s | %11.2f | %8.2f |\n",
	       trial_string, heads_string, tails_string,
	       chi_squared(num_heads, num_tails),
	       (double)(end_time - start_time));

        trial_flips *= 2;
    }
    
    printf(" -----------------------------------"
	   "------------------------------------\n");

    clean_exit(0);

    return 0;
}


double chi_squared(int heads, int tails) {
    double sum = 0;              // chi square sum
    double tot = heads + tails;  // total flips
    double expected = 0.5 * tot; // expected heads (or tails)
    
    sum = ((heads - expected) * (heads - expected) / expected) + 
	  ((tails - expected) * (tails - expected) / expected);
    
    return sum;
}


int pretty_int(int n, char* s) {
    int digit;	                    /* Each digit of n.          */  
    int digit_cnt = STRING_LEN - 1; /* Don't touch EOS character */

    if (NULL == s)
        return -1;

    do {
    	digit = n % 10;
    	n = n / 10;

	if (0 == digit_cnt % 4 && digit_cnt != 0) {
	    s[digit_cnt - 1] = ',';
	    digit_cnt--;
	}

	s[digit_cnt - 1] = '0' + digit;

	digit_cnt--;

    } while (n > 0);

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

    for (i = 0; i < STRING_LEN - 2; i++) {
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
