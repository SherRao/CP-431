#include <stdio.h>
#include <stdlib.h>
#include <mpi.h>
#include <gmp.h>

#define MAX_PRIME 1000000000 // 10^9

#define ulint unsigned long

typedef struct GapRank {
	ulint gap;
	int rank;
} GapRank;

/* Prototypes */
void print_mpz(char tag[], mpz_t n, char end[]);

/* Print Function */
void print_mpz(char tag[], mpz_t n, char end[]) {
	printf("%s = ", tag);
	mpz_out_str(stdout, 10, n);
	printf("%s", end);
}

/* Main Function */
int main(int argc, char** argv) {
	// Initialize the MPI environment
	int rank, size;

	// Initialize mpz_t variables
	mpz_t N;
	mpz_init(N);
	mpz_set_ui(N,MAX_PRIME);

	// Declare timer variables
	double first_time, second_time, duration, global_duration;

	// Declare prime variables
	mpz_t start, end, gap, prime, prev, load;

	// Initialize above mpz_t variables and set initial values
	mpz_init(start);
	mpz_init(end);
	mpz_init(gap);
	mpz_init(prime);
	mpz_init(prev);
	mpz_init(load);

	mpz_set_ui(start,0);
	mpz_set_ui(end,0);
	mpz_set_ui(gap,0);
	mpz_set_ui(prime,2);
	mpz_set_ui(prev,2);
	mpz_set_ui(load,0);

	MPI_Init(&argc, &argv);
	MPI_Comm_size(MPI_COMM_WORLD, &size);
	MPI_Comm_rank(MPI_COMM_WORLD, &rank);

	// Declare the start and end values of process
	mpz_div_ui(load, N, size);
	mpz_mul_ui(start, load, rank);
	mpz_add(end, start, load);

	// Store largest gap and the prime associated with it & first and last primes in this process
	mpz_t local_primegap[2]; 
	mpz_t first_last_primes[2]; 
	GapRank gap_rank;
	unsigned long first_last_primes_ui[2];

	// Find the first prime in this process to initialize first_last_primes[]
	mpz_nextprime(prime, start);
	mpz_set(prev, prime);

	// mpz_init() above arrays
	for (int i = 0; i < 2; ++i) {
		mpz_init(local_primegap[i]);
		mpz_init(first_last_primes[i]);
	}

	mpz_set(local_primegap[0], gap);
	mpz_set(local_primegap[1], prime);

	mpz_set(first_last_primes[0], prime);

	// Start timer
	first_time = MPI_Wtime();

	while (1) {
		mpz_nextprime(prime, prime);

		// Break loop if prime > end. Record the last prime encountered
		if (mpz_cmp(prime, end) > 0) {
			mpz_set(first_last_primes[1], prev);
			break;
		}

		// Calculate the gap between current and previous prime
		mpz_sub(gap, prime, prev);

		// If this is the largest gap, then record it and the associated prime
		if (mpz_cmp(gap, local_primegap[0]) >= 0) {
			mpz_set(local_primegap[0], gap);
			mpz_set(local_primegap[1], prime);
		}

		// Update previous prime to currrent prime
		mpz_set(prev, prime);
	}

	// End timer
	second_time = MPI_Wtime();
	duration = second_time - first_time;
	printf("rank = %d, local duration = %lf\n", rank, duration);

	// Send first and last primes to root thread
	first_last_primes_ui[0] = mpz_get_ui(first_last_primes[0]);
	first_last_primes_ui[1] = mpz_get_ui(first_last_primes[1]);

	if (rank != 0) {
		MPI_Send(first_last_primes_ui, 2, MPI_UNSIGNED_LONG, 0, 1, MPI_COMM_WORLD);
		ulint temp = mpz_get_ui(local_primegap[1]);
		MPI_Send(&temp, 1, MPI_UNSIGNED_LONG, 0, 2, MPI_COMM_WORLD);
	}

	// Get the local largest gap and associated prime in the form of unsigned long
	gap_rank.gap = mpz_get_ui(local_primegap[0]);
	gap_rank.rank = rank;

	// Find the max of all the local largest gaps, and the rank of the process it is in
	GapRank global_gap_rank;
	MPI_Reduce(&gap_rank, &global_gap_rank, 1, MPI_LONG_INT, MPI_MAXLOC, 0, MPI_COMM_WORLD);

	// Find the max of time taken by any thread
	MPI_Reduce(&duration, &global_duration, 1, MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);

	// Find the gaps between first primes of a process and last primes of the preceding process
	if (rank == 0) {
		
		ulint global_primegap[2];
		global_primegap[0] = global_gap_rank.gap;

		MPI_Recv(&global_primegap[1], 1, MPI_UNSIGNED_LONG, global_gap_rank.rank, 2, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
		// Declare array to store first and last primes from all processes
		unsigned long all_first_last_primes[size*2];

		// Store the first and last primes from root process
		all_first_last_primes[0] = first_last_primes_ui[0];
		all_first_last_primes[1] = first_last_primes_ui[1];

		// Receive first and last primes from other processes and store them
		MPI_Status status;
		for (int i = 1; i < size; ++i) {
			MPI_Recv(first_last_primes_ui, 2, MPI_UNSIGNED_LONG, i, 1, MPI_COMM_WORLD, &status);
			all_first_last_primes[i*2] = first_last_primes_ui[0];
			all_first_last_primes[i*2+1] = first_last_primes_ui[1];
		}

		// Find the difference between consecutive elements (ignore first and last elements).
		// If diff > largest gap, then recognize it
		unsigned long diff;
		for (int i = 2; i < size*2-1; i+=2) {
			diff =  all_first_last_primes[i] - all_first_last_primes[i-1];
			if (diff > global_primegap[0]) {
				global_primegap[0] = diff;
				global_primegap[1] = all_first_last_primes[i];
			}
		}

		// Output the largest gap and the associated prime
		printf("max gap = %lu, between %lu and %lu\n", global_primegap[0], global_primegap[1]-global_primegap[0], global_primegap[1]);
		printf("global runtime is %f\n", global_duration);
	}

	// End MPI Program
	MPI_Finalize();

	return 0;
}