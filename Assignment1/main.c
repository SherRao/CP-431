#include <stdio.h>
#include <math.h>
#include "main.h"
#include "mpi.h"
#include "gmp.h"

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
    {
        mainProcess();
    }
    else
    {
        childProcess(rank);
    }

    MPI_Finalize();
}

void mainProcess()
{
    collectResults();
}

void childProcess(int rank)
{
    int start;
    int end;
    int a;
    int b;
    int gap;
    calculateLargestPrimeDiff(rank, &start, &end, &a, &b, &gap);

    char message[1000];
    sprintf(message, "%d,%d,%d,%d,%d", start, end, a, b, gap);
    MPI_Send(message, 100, MPI_CHAR, 0, tag, MPI_COMM_WORLD);
}

void calculateLargestPrimeDiff(int rank, int *smallestPrime, int *largestPrime, int *a, int *b, int *gap))
{
    long unsigned int divisions = MAX_PRIME / processes;
    long unsigned int rangeStart = (rank - 1) * divisions;
    long unsigned int rangeEnd = rank * divisions;

    long unsigned int primeGapStart = -1;
    long unsigned int primeGapEnd = -1;
    long unsigned int primeGap = -1;

    mpz_t a;
    mpz_init(a);
    mpz_set_ui(a, rangeStart);
    mpz_nextprime(a, a);

    mpz_t b;
    mpz_init(b);
    mpz_set_ui(b, a);
    mpz_nextprime(b, b);

    while (b < rangeEnd)
    {
        int gap = b - a;
        printf("Prime gap for %d and %d: %d", a, b, gap);
        if (gap > primeGap)
        {
            primeGapStart = a;
            primeGapEnd = b;
            primeGap = gap;
        }

        mpz_nextprime(a, a);
        mpz_nextprime(b, b);
    }

    // TODO: mpz_nextprime
    *smallestPrime = rangeStart;
    *largestPrime = rangeEnd;
    *a = primeGapStart;
    *b = primeGapEnd;
    *gap = primeGap;
}

void collectResults()
{
    int resultStart;
    int resultEnd;
    int resultGap;

    int edgePrimeStarts[processes] = {0};
    int edgePrimeEnds[processes] = {0};
    int primeGapStarts[processes] = {0};
    int primeGapEnds[processes] = {0};
    int primeGaps[processes] = {0};

    int status;
    char message[1000];

    // Receive messages from child processe and store the data
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

    // Find the largest prime gap
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

    // Find the largest edge prime gap
    // TODO: Fix logic.
    int largestEdgePrimeGap = -1;
    int largestEdgePrimeGapStart = -1;
    int largestEdgePrimeGapEnd = -1;
    for (int i = 1; i < processes; i++)
    {
        int gap = edgePrimeEnds[i] - edgePrimeStarts[i];
        if (gap > largestEdgePrimeGap)
        {
            largestEdgePrimeGap = gap;
            largestEdgePrimeGapStart = edgePrimeStarts[i];
            largestEdgePrimeGapEnd = edgePrimeEnds[i];
        }
    }

    // Compare the largest prime gap and the largest edge prime gap
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
