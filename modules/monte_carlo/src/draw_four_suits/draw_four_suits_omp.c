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
#include "draw_four_suits_omp.h"


int main() {
    int total = 0;     // number of  hands yielding 4 suits
    int num_tests = 8; // number of trials in each run
    int i;	       // loop control variable
    int tid;           // thread id
    double percentage; // % of hands with 4 suits
    double start_time; 
    double stop_time;
    char tests_string[] = {' ', ' ', ' ', ' ', ' ', ' ', 
			   ' ', ' ', ' ', ' ', ' ', ' ', '\0'};

    // print heading info...
    printf("\n Starting simulation...\n\n");
    printf(" --------------------------------------\n");
    printf(" | number of draws | percent of draws |\n");
    printf(" |                 |  with four suits |\n");
    printf(" --------------------------------------\n");

    start_time = omp_get_wtime();

    while (num_tests < ITERATIONS) {
	total = 0; //reset counter
	
        #pragma omp parallel num_threads(NUM_THREADS) default(none) \
	private (i, tid) shared (num_tests, seeds) reduction (+:total)
	{
	    tid = omp_get_thread_num();
	    seeds[tid] = abs( ( ( time(NULL) * 181) * (tid - 83) * 359 )
			      % 104729 );

            #pragma omp for schedule(dynamic)
	    for (i = 0; i < num_tests; i++) { 
		// make new deck - pick hand - test for 4 suits
		if (test_one_hand(tid)) {
		    total ++;
		}
	    }
	}

	// calc % of 4-suit hands & report results...
	percentage = 100.0 * ( (double)total) / num_tests;
	pretty_int(num_tests, tests_string);
	printf(" | %15s | %15.2f%% |\n", tests_string, percentage);
	num_tests += num_tests;
    }

    stop_time = omp_get_wtime();

    printf(" --------------------------------------\n\n");
    printf(" Elapsed wallclock time: %.2f seconds\n\n",
	   (double)(stop_time - start_time));
    printf(" *** Normal Termination ***\n\n");

    return 0;
}


int rand_int_between(int low, int hi, int tid){
    return rand_r(&seeds[tid]) % (hi - low + 1) + low;
}


void shuffle_deck(int deck[], int num_cards, int tid) {
    int num_in_fifth = num_cards / 5;
    int low = num_in_fifth * 2;
    int hi  = low + num_in_fifth - 1;
    int mid = rand_int_between(low, hi, tid);
    int lowIndex = 0;   // start of LO half
    int hiIndex  = mid; // start of HIGH half
    int index    = 0;   // loc in 'shuffled' deck
    int temp[num_cards];
    int i;

    // FSM to simulate fanning shuffle
    enum STATE my_state = MERGE2;

    for (i = 0; i < num_cards; i++)
	temp[i] = deck[i];

    // FSM simulates a fanning-type shuffle
    while (my_state != DONE) {
	switch (my_state) {
	case MERGE2:
	    if (rand_r(&seeds[tid]) % 2 > 0) {
		deck[index] = temp[lowIndex];
		lowIndex++;
		if (lowIndex >= mid) {
		    my_state = FLUSH_HIGH;
		}
	    } else {
		deck[index] = temp[hiIndex];
		hiIndex++;
		if (hiIndex >= num_cards) {
		    my_state = FLUSH_LOW;
		}
	    }
	    index++;
	    break;
	case FLUSH_LOW:
	    while (index < num_cards) {
		deck[index] = temp[lowIndex];
		lowIndex++;
		index++;
	    }
	    my_state = DONE;
	    break;
	case FLUSH_HIGH:
	    while (index < num_cards) {
		deck[index] = temp[hiIndex];
		hiIndex++;
		index++;
	    }
	    my_state = DONE;
	    break;
	default:
	    printf("\nBad state in FSM\n");
	    return;
	}
    }
}


void init_deck(int deck[], int tid){
    int i;

    for (i = 0; i < DECK_SIZE; i++) {
	deck[i] = i;
    }

    for (i = 0; i < NUM_SHUFFLES; i++) {
	shuffle_deck(deck, DECK_SIZE, tid);
    }
}


int pick_card (int deck[], int *num_cards, int tid){
    int loc = rand_int_between(0, (*num_cards) - 1, tid);
    int card = deck[loc];
    int i;

    for (i = loc + 1; i < (*num_cards); i++) {
	deck[i - 1] = deck[i];
    }

    (*num_cards)--;

    return card;
}


int test_one_hand(int tid){
    int deck[DECK_SIZE];
    int hand[CARDS_IN_HAND];
	
    init_deck(deck, tid); //create & shuffle a new deck
	
    draw_hand(deck, hand, tid); //go pick cards from deck
	
    return is_four_suits(hand); //test if 4 suits
}


void draw_hand(int deck[], int hand[], int tid){
    int i;
    int num_cards = DECK_SIZE;
    int card;

    for (i = 0; i < CARDS_IN_HAND; i++) {
	card = pick_card(deck, &num_cards, tid);
	hand[i] = card;
    }
}


int find_greatest(int ary[], int n) {
    int big = ary[0]; // assume 1st is greatest
    int i;

    for (i = 1; i < n; i++) {
	if (ary[i] > big) { 
	    big = ary[i];
	}
    }
	
    return big;
}


int is_four_suits(int hand[]){
    int temp[4] = {0};
    int i;

    // copy cards, converting to suit values
    for (i = 0; i < CARDS_IN_HAND; i++) {
	int suit = hand[i] / 13;
	temp[suit]++; //count the suits represented
    }
	
    // if largest suits == 1 then all 4 suits counted in 4 cards
    return (1 == find_greatest(temp, 4));
}

int pretty_int(int n, char* s) {
    int digit;	        // each digit of n
    int digit_cnt = 11; // count by 3's for comma insert

    if (NULL == s) {
        return -1;
    }

    do {
    	digit = n % 10; // get lsd
    	n = n/10;    	// and chop it from n

	if (8 == digit_cnt || 4 == digit_cnt) {
	    s[digit_cnt] = ',';
	    digit_cnt--;
	}

	s[digit_cnt] = '0' + digit;

	digit_cnt--;

    } while (n > 0);

    return 0;
}
