/*
 * Sequential simulation of a roulette wheel.
 *
 * American wheel has 38 slots:
 *  -2 are 'green' (0 & 00)
 *   house ALWAYS wins on green
 *  -18 are red (1..18)
 *  -18 are black (1..18)
 *  -Our user always bets "red"
 *  -Odds should be:  18/38 or 47.37%
 *
 * History:
 *  Dave Valentine (Slippery Rock University): Original C++ program
 *  Libby Shoop    (Macalester University)   : Adapted for CS in
 *                                             Parallel Module
 *  Justin Ragatz  (UW-La Crosse)            : Adapted for OnRamp Module
 *                                             rewritten in C.
 */

#include "roulette_sim_omp.h"


int main() {
    int num_spins = 1; // spins per trial
    int	num_wins;      // wins per trial
    double start_time;
    double end_time;

    printf("\n Starting simulation...\n\n");
    printf(" ---------------------------------------------------\n");
    printf(" | Number of spins | Number of wins | Percent wins |\n");
    printf(" ---------------------------------------------------\n");

    start_time = omp_get_wtime();

    /*
     * begin simulation
     */		
    while (num_spins < MAX) {
	// spin wheel
	num_wins = get_num_wins(num_spins);
	// print results
	show_results(num_spins, num_wins);
	// double spins for next simulation
	num_spins += num_spins;
    }

    end_time = omp_get_wtime();

    /*
     * all done
     */
    printf(" ---------------------------------------------------\n\n");
    printf(" Elapsed wall clock time: %7.2f\n\n",
	   (double)(end_time - start_time));
    printf(" *** Normal Termination ***\n\n");
    
    return 0;
}


int get_num_wins(int num_spins) {
    int wins = 0;    // win counter
    int spin = 0;    // loop control variable
    int my_bet = 10; // amount we bet per spin
    int tid;

    #pragma omp parallel num_threads(N_THREADS) default(none) \
    shared(num_spins, my_bet, seeds) \
    private(spin, tid) \
    reduction(+:wins)
    {
	tid = omp_get_thread_num();
	seeds[tid] = abs( ( ( time(NULL) * 181) * (tid - 83) * 359 ) % 104729 );

        #pragma omp for
	for (spin = 0; spin < num_spins; spin++) {
	    if (spin_red(my_bet, tid) > 0) {
		wins++;
	    }
	}
    }
	
    return wins;
}


int spin_red(int bet, int tid) {
    int payout = -1;
    int slot = rand_int_between(1, 38, tid);

    /*
     *  0..17 red   - win
     * 18..36 black - lose
     * else   green - lose half
     */
    if (slot <= 18) {
    	payout = bet;
    } else if (slot <= 36) {
    	payout = -bet;
    } else {
    	payout = -(bet/2);
    }

    return payout;
}


int pretty_int(int n, char* s) {

    int digit;
    int digit_cnt = 11;

    if (NULL == s) {
        return -1;
    }

    do {
    	digit = n % 10;
    	n = n/10;

	if (8 == digit_cnt || 4 == digit_cnt) {
	    s[digit_cnt] = ',';
	    digit_cnt--;
	}

	s[digit_cnt] = '0' + digit;

	digit_cnt--;

    } while (n > 0);

    return 0;
}


void show_results(int num_spins, int num_wins){

    char spins_string[] = {' ', ' ', ' ', ' ', ' ', ' ', 
			   ' ', ' ', ' ', ' ', ' ', ' ', '\0'};
    char wins_string[]  = {' ', ' ', ' ', ' ', ' ', ' ',
			   ' ', ' ', ' ', ' ', ' ', ' ', '\0'};
    double percent = 100.0 * (double)num_wins / (double)num_spins;

    pretty_int(num_spins, spins_string);
    pretty_int(num_wins,  wins_string);

    printf(" | %15s | %14s | %11.2f%% |\n", spins_string, wins_string, percent);
}


int rand_int_between(int low, int hi, int tid) {
    return rand_r(&seeds[tid]) % (hi - low + 1) + low;
}
