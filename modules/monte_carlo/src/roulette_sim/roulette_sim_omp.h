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

#include <stdio.h>
#include <time.h>
#include <string.h>
#include <stdlib.h>
#include <omp.h>

/***************************************
* Defines
***************************************/

#define MAX 1<<20   // limit to number of spins
#define N_THREADS 4 // the number of threads to use

/***************************************
* Global Variables
***************************************/

unsigned int seeds[N_THREADS];

/***************************************
* Function Declarations
***************************************/

/*
 * Counts the total number of wins for a given number of spins.
 *
 * Parameters:
 *  num_spins: number of times to spin wheel
 *
 * Returns:
 *  wins: number of wins
 */
int get_num_wins(int num_spins);


/*
 * Determine the payout after spinning wheel for a certain bet.
 *
 * Paramters:
 *  bet: amount bet
 *  tid: thread id
 *
 * Returns:
 *  payout: the payout based on the bet and outcome of the spin
 */
int spin_red(int bet, int tid);


/*
 * Print results so far to the console.
 *
 * Parameters:
 *  num_spins: total number of spins
 *  num_wins: total number of wins
 */
void show_results(int num_spins, int num_wins);


/*
 * Convert an int to a comma-delimited string.
 *
 * Parameters:
 *  n: the int to be converted
 *  s: the resulting comma-delimited string (pass by reference)
 *
 * Returns"
 *  0: success
 *  -1: s is NULL
 */
int pretty_int(int n, char* s);


/*
 * Generates a random number between two values.
 *
 * Parameters:
 *  low: lower limit
 *  high: upper limit
 *  tid: thread id, so we know what seed to use
 *
 * Returns:
 *  the random number that was generated
 */
int rand_int_between(int low, int hi, int tid);
