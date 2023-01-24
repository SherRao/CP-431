#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "mpi.h"
#include "gmp.h"

#define MAX_PRIME 1000000000000
#define ulint unsigned long int
#define tag 1000

void childProcess(int);
void mainProcess(int);
void collectResults(int);
void calculateLargestPrimeDiff(int, ulint *, ulint *, ulint *, ulint *, ulint *);

int main(int argc, char **argv)
{
    int processes;
    int rank;
    if (MPI_Init(&argc, &argv) != MPI_SUCCESS)
    {
        printf("MPI_Init failed!");
        exit(0);
    }

    MPI_Comm_size(MPI_COMM_WORLD, &processes);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    if (rank == 0)
        mainProcess(processes);

    else
        childProcess(rank);

    MPI_Finalize();
}

void mainProcess(int processes)
{
    collectResults(processes);
}

void childProcess(int rank)
{
    ulint smallestPrime;
    ulint largestPrime;
    ulint largestPrimeGapStart;
    ulint largestPrimeGapEnd;
    ulint largestPrimeGap;
    calculateLargestPrimeDiff(rank, &smallestPrime, &largestPrime, &largestPrimeGapStart, &largestPrimeGapEnd, &largestPrimeGap);

    char message[1000];
    sprintf(message, "%lu,%lu,%lu,%lu,%lu", smallestPrime, largestPrime, largestPrimeGapStart, largestPrimeGapEnd, largestPrimeGap);
    MPI_Send(message, 100, MPI_CHAR, 0, tag, MPI_COMM_WORLD);
}

void calculateLargestPrimeDiff(int rank, ulint *smallestPrime, ulint *largestPrime, ulint *largestPrimeGapStart, ulint *largestPrimeGapEnd, ulint *largestPrimeGap)
{
    ulint divisions = MAX_PRIME / processes;
    ulint rangeStart = (rank - 1) * divisions;
    ulint rangeEnd = rank * divisions;

    ulint primeGapStart = -1;
    ulint primeGapEnd = -1;
    ulint primeGap = -1;

    mpz_t a;
    mpz_init(a);
    mpz_set_ui(a, rangeStart);
    mpz_nextprime(a, a);
    *smallestPrime = a;

    mpz_t b;
    mpz_init(b);
    mpz_set_ui(b, a);
    mpz_nextprime(b, b);

    while (b < rangeEnd)
    {
        *largestPrime = b;
        int gap = b - a;
        printf("Prime gap for %d and %d: %d", a, b, gap);
        if (gap > primeGap)
        {
            *largestPrimeGapStart = a;
            *largestPrimeGapEnd = b;
            *largestPrimeGap = gap;
        }

        mpz_set_ui(a, b);
        mpz_nextprime(b, b);
    }
}

void collectResults(int processes)
{
    int resultStart;
    int resultEnd;
    int resultGap;

    int edgePrimeStarts[processes] = malloc(sizeof(int) * processes);
    int edgePrimeEnds[processes] = malloc(sizeof(int) * processes);
    int primeGapStarts[processes] = malloc(sizeof(int) * processes);
    int primeGapEnds[processes] = malloc(sizeof(int) * processes);
    int primeGaps[processes] = malloc(sizeof(int) * processes);

    int *status;
    char message[1000];

    // Receive messages from child processes and store the data.
    for (int i = 1; i < processes; i++)
    {
        MPI_Recv(message, 100, MPI_CHAR, i, tag, MPI_COMM_WORLD, &status);
        int rangeStart = atoi(strtok(message, ","));
        int rangeEnd = atoi(strtok(NULL, ","));
        int primeGapStart = atoi(strtok(NULL, ","));
        int primeGapEnd = atoi(strtok(NULL, ","));
        int primeGap = atoi(strtok(NULL, ","));

        edgePrimeStarts[i] = rangeStart;
        edgePrimeEnds[i] = rangeEnd;
        primeGapStarts[i] = primeGapStart;
        primeGapEnds[i] = primeGapEnd;
        primeGaps[i] = primeGap;
    }

    // Find the largest prime gap.
    int largestPrimeGap = -1;
    int largestPrimeGapStart = -1;
    int largestPrimeGapEnd = -1;
    for (int i = 1; i < processes; i++)
    {
        if (primeGaps[i] > largestPrimeGap)
        {
            largestPrimeGap = primeGaps[i];
            largestPrimeGapStart = primeGapStarts[i];
            largestPrimeGapEnd = primeGapEnds[i];
        }
    }

    // Find the largest edge prime gap.
    // Ignore the first start edge prime gap.
    int largestEdgePrimeGap = -1;
    int largestEdgePrimeGapStart = -1;
    int largestEdgePrimeGapEnd = -1;
    for (int i = 0; i < processes - 1; i++)
    {
        int gap = edgePrimeEnds[i] - edgePrimeStarts[i + 1];
        if (gap > largestEdgePrimeGap)
        {
            largestEdgePrimeGap = gap;
            largestEdgePrimeGapStart = edgePrimeStarts[i];
            largestEdgePrimeGapEnd = edgePrimeEnds[i + 1];
        }
    }

    // Compare the largest prime gap and the largest edge prime gap.
    if (largestPrimeGap > largestEdgePrimeGap)
    {
        resultGap = largestPrimeGap;
        resultStart = largestPrimeGapStart;
        resultEnd = largestPrimeGapEnd;
    }
    else
    {
        resultGap = largestEdgePrimeGap;
        resultStart = largestEdgePrimeGapStart;
        resultEnd = largestEdgePrimeGapEnd;
    }
}
