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

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <omp.h>
#include <ctype.h>

/***************************************
* Defines
***************************************/

#define TRIALS          18
#define FLIPS_PER_TRIAL 256
#define STRING_LEN      12
#define N_THREADS       4

/***************************************
* Global Variables
***************************************/

char* trial_string;
char* heads_string;
char* tails_string;
unsigned int seeds[N_THREADS];

/***************************************
* Function Declarations
***************************************/

/*
 * Standard Chi Squared Test. This statisical hypothesis test, tells us
 * whether there is a significant difference between the expected and
 * observed frequency of an event.
 *
 * Parameters:
 *  heads: Number of coin flips resulting in 'heads'.
 *  tails: Number of coin flips resulting in 'tails'.
 *
 * Returns:
 *  Sum of the squared differnece between the observed and expected
 *  data, divided by the total expected data.
 */
double chi_squared(int heads, int tails);


/*
 * Convert an int into a comma-delimited string.
 *
 * Parameters:
 *  n: The number to be converted.
 *  s: The resulting comma-delimited string.
 *
 * Returns:
 *  0 on success
 * -1 on failure
 */
int pretty_int(int n, char* s);


/*
 * Allocate memory for, error-check, and initialize the three global
 * strings: trials_string, tails_string, and heads_string. These arrays
 * are declared in the globals section. The amount of memory allocted
 * for all of these arrays depends on the value of STRING_LEN. This
 * value is found in the #define section. The default value of 12 allows
 * for numbers up to 999,999,999 to be printed.
 * 
 * Returns:
 *  0 on success
 * -1 on failure
 */
int create_strings();


/*
 * Free all memory allocated using malloc. If the value of STATUS is
 * non-zero, then the function will print the message 'Terminated by
 * error' to stderr and exits with status EXIT_FAILURE. If the value of
 * status is 0, then the message 'Normal termination' is printed and the
 * function returns 0. 
 *
 * Parameters:
 *  0 if calling due to normal termination.
 * -1 if calling due to an error.
 *
 * Returns:
 *  0 on success
 * -1 on failure
 */
int clean_exit(int status);
