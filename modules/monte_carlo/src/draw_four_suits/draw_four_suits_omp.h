/*
 * This program simulates the probability of being dealt all suits,
 * for a hand of four cards.
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
#include <math.h>
#include <time.h>
#include <string.h>
#include <omp.h>

/***************************************
* Defines
***************************************/

#define DECK_SIZE 52     // std deck of cards
#define ITERATIONS 1<<20 // max iterations is 1 meg
#define CARDS_IN_HAND 4  // draw 4 cards at a time
#define NUM_SHUFFLES 10  // num times to shuffle new deck
#define NUM_THREADS 4    // number of threads to use

/***************************************
* Global Variables
***************************************/

unsigned int seeds[NUM_THREADS];

enum STATE {
    MERGE2,
    FLUSH_HIGH,
    FLUSH_LOW,
    DONE,
};

/***************************************
* Function Declarations
***************************************/

/*
 * Generate random number within range [low...hi].
 *
 * Parameters:
 *  low: lower limit
 *  hi: upper limit
 *  tid: thread id
 *
 * Returns
 *  random int within [low...hi]
 */
int rand_int_between(int low, int hi, int tid);


/*
 * Simulate fanning shuffle.
 *
 * Parameters:
 *  deck: deck of cards
 *  num_cards: number of cards in deck
 *  tid: thread id
 */
void shuffle_deck(int deck[], int num_cards, int tid);

/*
 * Load the card values and shuffle the deck.
 *
 * Parameters:
 *  deck: the deck of cards
 *  tid: thread_id
 */
void init_deck(int deck[], int tid);


/*
 * Randomly select one card from the deck.
 *
 * Paramters:
 *  deck: the deck of cards
 *  num_cards: the number of cards in the deck
 *  tid: thread id
 *
 * Returns:
 *  value of card selected
 */
int pick_card (int deck[], int *num_cards, int thread_id);


/*
 * Create a deck, shuffle it, pick four cards, and test if
 * all four are of a different suit.
 *
 * Paramters:
 *  tid: the thread id
 *
 * Returns:
 *  1: all four suits are present
 *  0: not all four suits are present
 */
int test_one_hand(int tid);


/*
 * Select five random cards from the deck, without replacing them.
 *
 * Parameters:
 *  deck: the deck of cards
 *  hand: cards in hand
 *  tid: thread id
 */
void draw_hand(int deck[], int hand[], int tid);


/*
 * Find the highest value card in array of size n.
 *
 * Paramters:
 *  ary: array of cards
 *  n: number of cards in the array
 *
 * Returns:
 *  the value of the highest value card in the array
 */
int find_greatest(int ary[], int n);


/*
 * Determine whether the hand contains all four suits.
 *
 * Paramters:
 *  hand: the current hand of cards
 *
 * Returns:
 *  1: all four suits are present
 *  0: not all four suits are present
 */
int is_four_suits(int hand[]);


/*
 * Convert an int to a comma-delimited string.
 *
 * Parameters:
 *  n: the int to be converted
 *  s: the resulting comma-delimited string (pass by reference)
 *
 * Returns"
 *  0: success
 * -1: s is NULL
 */
int pretty_int(int n, char* s);
