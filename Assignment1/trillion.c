#include <stdio.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>
#include <mpi.h>
#include <stdlib.h>
#include <pthread.h>

int segmentedSieve(long n, int first_primes[], int count, long start);

int SieveOfEratosthenes(long n, int lst[])
{
    float sqt = sqrt(n);
    int flr = floor(sqt) + 1;

    bool prime[flr + 1];
    memset(prime, true, sizeof(prime));

    int x = 0;
    int c = 0;

    for (int p = 2; p * p <= flr; p++)
    {
        if (prime[p] == true)
        {
            for (int i = p * p; i <= flr; i += p) {
                prime[i] = false;
                //lst[i] = false;
            }
        }
        x++;
    }

    for (int p = 2; p <= flr; p++)
        if (prime[p]) {
            lst[c] = p;
            c++;
        }

    return c;
}

int main()
{
    long n = 1000000000000;
    int largest_gap = 0;
    int G = 0;

    float sqt = sqrt(n);
    int flr = floor(sqt) + 1;
    
    printf("This is the biggest gap from one to %ld \n", n);
    int x[flr+1];

    memset(x, 0, sizeof x);

    int count = SieveOfEratosthenes(n, x);

    //block must be larger than root N 
    int block_size = 2000000;


    for (long i = block_size; i < n; i += block_size){
    if (i > n == false)
        G = segmentedSieve(block_size + i - 1, x, count, i);

        if (G > largest_gap)
        {
            largest_gap = G;

            printf("%d\n", largest_gap);
            G = 0;
        }
        if(i % 1000000000 == 0)
        printf("at: %ld\n", i);
   }

    return 0;
}

int segmentedSieve(long n, int first_primes[], int count, long start)
{
    //float sqt = sqrt(n);
    //int flr = floor(sqt) + 1;

    long limit = start;

    int gap = 0;
    int max_gap = 0;
    // a block of the primes all set to true ex [100..200]
    bool block[n - start + 1];//limit + 1];
    memset(block, true, sizeof(block));

    long low = limit;
    long high = 2 * limit;
    int c = 0;

    while (low < n)
    {
        if (high >= n)
            high = n;
        //c++;

        for (int i = 0; i < count; i++)
        {
            float temp = ((float)low) / ((float)first_primes[i]);
            long lowest_lim = floor(temp) * first_primes[i];

            if (lowest_lim < low)
            lowest_lim += first_primes[i];

            for (long j = lowest_lim; j < high; j += first_primes[i])
            block[j - low] = false;
        }

        low = low + limit;
        high = high + limit;
    }


    for (long i = 0; i <= n - start; i++)
    {
        if (block[i] == true)
        {
            if (max_gap < gap)
            max_gap = gap;
            gap = 0;
        }
        gap++;
    }
    return max_gap;
}