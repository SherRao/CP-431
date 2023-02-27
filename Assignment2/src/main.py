import numpy as np
import sys
import sort
import time
from mpi4py import MPI
from typing import Tuple

BIG_N = 100_000_00                          # The number of integers
MAX_INT = min(2_147_000_000, 10 * BIG_N)    # The range in which random ints are generated
PRINT_LIMIT = 20                            # Don't print arrays if size exceeds this value
SHOULD_CHECK_CORRECTNESS = False            # Check if the merged array is sorted - quite slow for large values of N


def generate_sorted_int_array(lower: int, upper: int, n: int, data_type: str ='i') -> np.ndarray:
    """
    Description:
        Generates a sorted array of random integers.

    Parameters:
        lower: The lower bound of the random integers.
        upper: The upper bound of the random integers.
        n: The number of random integers to generate.
        data_type: The data type of the array. Default is 'i' for int32.

    Returns:
        A sorted array of random integers.
    """
    return np.sort(np.random.randint(lower, upper, size=n, dtype=data_type))


def simple_merge(arr1: np.ndarray, arr2: np.ndarray) -> np.ndarray:
    """
    Description:
        Merges two sorted arrays into one sorted array.

    Parameters:
        arr1: The first sorted array.
        arr2: The second sorted array.

    Returns:
        A sorted array containing all elements of arr1 and arr2.
    """
    return np.sort(np.concatenate((arr1, arr2)), kind='merge')


def binary_search(arr: np.ndarray, elem: any, start: int) -> int:
    """
    Description:
        Performs a binary search on an array for a given element.

    Parameters:
        arr: The array to search.
        elem: The element to search for.
        start: The index to start the search from.

    Returns:
        The index of the element if it is found, or the index of the first
    """
    first = start
    last = len(arr)
    mid = (first + last) // 2
    while(first <= last):
        if(mid == len(arr) or arr[mid] == elem):
            return mid

        elif(arr[mid] < elem):
            first = mid + 1

        else:
            last = mid - 1

        mid = (first + last) // 2

    return mid + 1


def check_correctness(a: np.ndarray, b: np.ndarray, merged: np.ndarray) -> bool:
    """
    Description:
        Checks the correctness of the merged array by comparing it to the
        result of a simple merge of the two arrays, and prints the result.

    Parameters:
        a: The first sorted array.
        b: The second sorted array.
        merged: The merged array.

    Returns:
        True if the merged array is correct, False otherwise.
    """
    print("Checking for correctness...")
    is_correct = (merged == simple_merge(a, b)).all()
    print("Correct" if is_correct else "Incorrect")
    return is_correct


def root_process(comm: any, rank: int, size: int) -> None:
    """
    Description:
        The root process of the program. Generates two sorted arrays of random
        integers, then uses parallelisation to merge them into one sorted array.

    Parameters:
        None
    """
    def array_generation() -> Tuple[np.ndarray, np.ndarray]:
        """
        Description:
            Generates two sorted arrays of random integers.

        Parameters:
            None

        Returns:
            A tuple containing the two generated arrays.
        """
        gen_arr_time_start = MPI.Wtime()
        a = generate_sorted_int_array(0, MAX_INT, BIG_N)
        b = generate_sorted_int_array(0, MAX_INT, BIG_N)
        gen_arr_time_end = MPI.Wtime()

        print(f"The elements per array has been set to N = {BIG_N:,}.")
        print(f"Time to generate and sort arrays = {gen_arr_time_end - gen_arr_time_start: .4f} seconds.\n")
        print(f"The two generated arrays are of length {BIG_N}.")
        if(BIG_N < PRINT_LIMIT):
            print("The two arrays are:")
            print(f"A: {a}")
            print(f"B: {b}")

        else:
            print("The arrays are too large to print.")

        return a, b

    def parallel_merge(a, b) -> np.ndarray:
        """
        Description:
            Performs a parallel merge of the two arrays.

        Parameters:
            a: The first sorted array.
            b: The second sorted array.

        Returns:
            A sorted array containing all elements of a and b.
        """
        merge_start_time = MPI.Wtime()

        # Split the list into parts based on number of cores
        a_s = np.array_split(a, size - 1)
        for i in range(1, size):
            # tag 0 is an A list block
            comm.send(len(a_s[i-1]), dest=i, tag=3)
            comm.Send([a_s[i-1], MPI.INT], dest=i, tag=0)

        # O(n) search for break points in B to create blocks
        breaks = [0] * size
        for i, group in enumerate(a_s):
            b_index = sort.binary_search(b, group[-1], breaks[i])
            breaks[i+1] = b_index

        # Set last element to be the length of the array
        breaks[-1] = len(b)
        for i in range(1, size):
            # tag 1 is a B list block
            lower, upper = breaks[i-1], breaks[i]
            comm.send(len(b[lower:upper]), dest=i, tag=4)
            comm.Send([b[lower:upper], MPI.INT], dest=i, tag=1)

        marged = [None] * (size - 1)
        for i in range(1, size):
            # tag 5 is length of merged array, tag 6 is the merged array
            size = comm.recv(source=i, tag=5)
            merged = np.empty(size, dtype='i')
            comm.Recv([merged, MPI.INT], source=i, tag=6)
            marged[i-1] = merged

        marged = np.concatenate(marged, dtype='i')
        merge_end_time = MPI.Wtime()

        print(f'Size of merged array: {sys.getsizeof(marged) / 1_000_000: ,.2f} MB')
        print(f"Time to parallel merge = {merge_end_time - merge_start_time: .4f} seconds")
        if(BIG_N < PRINT_LIMIT):
            print(f"Merged: {marged}")

        return merged

    a, b = array_generation()
    merged = parallel_merge(a, b)
    if(SHOULD_CHECK_CORRECTNESS):
        check_correctness(a, b, merged)


def non_root_process(comm: any, rank: int, size: int) -> None:
    """
    Description:
        A non-root process of the program. Receives two sorted sub-arrays from the
        root process, merges them into one sorted array, and sends it back to the
        root process.

    Parameters:
        None
    """
    # Get an A block, first size then numpy array
    x: int = comm.recv(source=0, tag=3)
    data = np.empty(x, dtype='i')
    comm.Recv([data, MPI.INT], source=0, tag=0)

    # Get a B block of arbitrary size
    y: int = comm.recv(source=0, tag=4)
    datab = np.empty(y, dtype='i')
    comm.Recv([datab, MPI.INT], source=0, tag=1)

    # Merge data and datab
    #merged = simple_merge(data, datab)
    r = MPI.Wtime()
    merged = sort.sort(data, datab, x, y)
    t = MPI.Wtime()

    print("<>", t - r)
    # tag 5 is length of merged array, tag 6 is the merged array
    comm.send(merged.size, dest=0, tag=5)
    comm.Send([merged, MPI.INT], dest=0, tag=6)


def main():
    """
    Description:
        The main function of the program. Generates two sorted arrays of random
        integers, then uses parallelisation to merge them into one sorted array.

    Parameters:
        None
    """
    np.random.seed(round(time.time() * 1000))

    # Basic setup for MPI stuff.
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    if rank == 0:
        root_process(comm, rank, size)

    elif rank >= 1:
        non_root_process(comm, rank, size)

    return
