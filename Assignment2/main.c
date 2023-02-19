#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include "mpi.h"

/**
 * @brief The main function.
 *
 * @param argc The number of arguments
 * @param argv The arguments
 * @return int The exit code
 */
int main(int argc, char **argv)
{
    srand(time(NULL));
    int *A = generateRandomArray(100);
    int *B = generateRandomArray(100);
    start(A, B);
    return 0;
}

int start(int[] A, int[] B)
{
    int processes;
    int rank;
    if (MPI_Init(&argc, &argv) != MPI_SUCCESS)
    {
        printf("MPI_Init failed!\n");
        exit(0);
    }

    MPI_Comm_size(MPI_COMM_WORLD, &processes);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    if (rank == 0)
        mainProcess(processes);

    else
        childProcess(rank, processes);

    MPI_Finalize();
}

void parallelMergeSortedArrays(int rank, int processes, int[] A, int[] B)
{
    int *combinedArray = malloc((A.length + B.length) * sizeof(int));
    memcpy(combinedArray, A, A.length * sizeof(int));
    memcpy(combinedArray + A.length, B, B.length * sizeof(int));

    int start = rank * (A.length / processes);
    int end = (rank + 1) * (A.length / processes);
    int *subArray = getSubArray(combinedArray, start, end);
}

/**
 * @brief Generates a random array of integers.
 *
 * @param size The size of the array
 * @return int* The array
 * @note The array is allocated on the heap, so it must be freed
 */
int *generateRandomArray(int size)
{
    int *array = malloc(size * sizeof(int));
    for (int i = 0; i < 100; i++)
        array[i] = rand() % 10000;

    return array;
}

/**
 * @brief Gets a sub array from an array.
 *
 * @param arr The array
 * @param start The start index
 * @param end The end index
 * @return int* The sub array
 * @note The sub array is allocated on the heap, so it must be freed
 */
int *getSubArray(int[] arr, int start, int end)
{
    int[] subArray = new int[end - start];
    for (int i = start; i < end; i++)
        subArray[i - start] = arr[i];

    return subArray;
}
