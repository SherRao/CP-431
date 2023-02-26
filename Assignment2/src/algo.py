import numpy as np
from mpi4py import MPI
import sys

BIG_N = 1_000_000_000 # The number of integers
MAX_INT = 10 * BIG_N # The range in which random ints are generated
PRINT_LIMIT = 20 # Don't print arrays if size exceeds this value

SEED = 50 # For numpy array generation
np.random.seed(SEED)

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def binary_search(arr, elem, start):
    first = start
    last = len(arr)
    mid = int((first + last)/2)
    
    while first <= last:
        if (mid == len(arr) or arr[mid] == elem):
            return mid
        elif arr[mid] < elem:
            first = mid + 1
        else:
            last = mid - 1

        mid = int((first + last)/2)

    return mid + 1

def generate_sorted_randint_array(lower, upper, n, dtype):
    return np.sort(np.random.randint(lower, upper, size=n, dtype=dtype))

if rank == 0:
    # Generate to randomly sorted lists
    print(f"N = {BIG_N:,}")

    sort_time_start = MPI.Wtime()
    a = generate_sorted_randint_array(0, MAX_INT, BIG_N, 'int64')
    b = generate_sorted_randint_array(0, MAX_INT, BIG_N, 'int64')
    sort_time_end = MPI.Wtime()
    print(f"Time to generate and sort arrays = {sort_time_end - sort_time_start: .4f} seconds")

    # print arrays if they are small
    if (BIG_N < PRINT_LIMIT):
        print("A:      ", a)
        print("B:      ", b)

    merge_start_time = MPI.Wtime()
		
    # Split the list into parts based on number of cores
    a_s = np.array_split(a, size - 1)
    
    for i in range(1, size) :
        # tag 0 is an A list block
        comm.send( len(a_s[i-1]) , dest=i, tag=3)
        comm.Send([ a_s[i-1] , MPI.INT], dest=i, tag=0)
    
    # O(n) search for break points in B to create blocks
    # initialize all elements to be length of b, and set first element to be 0
    breaks = [len(b)]*size 
    breaks[0] = 0

    for i, group in enumerate(a_s):
        b_index = binary_search(b, group[-1], breaks[i])
        breaks[i+1] = b_index

    breaks[-1] = len(b)
    
    for i in range(1, size):
        # tag 1 is a B list block
        lower, upper = breaks[i-1], breaks[i]
        comm.send(len(b[lower:upper]), dest=i, tag=4)
        comm.Send([b[lower:upper], MPI.INT], dest=i, tag=1)
    
    # receive merged arrays.
    merged_arrays = [None] * (size-1)
    for i in range(1,size):
        # tag 5 is length of merged array, tag 6 is the merged array
        size = comm.recv(source=i, tag=5) 
        merged = np.empty( size, dtype='int64')
        comm.Recv([merged, MPI.INT], source=i, tag=6)
        merged_arrays[i-1] = merged
    
    merged_arrays = np.concatenate(merged_arrays, dtype = 'int64')

    merge_end_time = MPI.Wtime()
    
    
    if (BIG_N < PRINT_LIMIT):
        print("Merged: ", merged_arrays, merged_arrays.shape)
    print(f"Time to parallel merge = {merge_end_time - merge_start_time: .4f} seconds")
    
    print("Checking for correctness:", end=" ")
    simple_merged = np.sort(np.concatenate((a,b)), kind='merge')
    correct = "Correct" if ((merged_arrays==simple_merged).all()) else "Incorrect"
    print(correct)


elif rank >= 1:
    # Get an A block, first size then numpy array
    x = comm.recv(source=0, tag=3)
    data = np.empty( x , dtype='int64')
    comm.Recv([data, MPI.INT], source=0, tag=0)
    
    #Get a B block of arbitrary size
    y = comm.recv(source=0, tag=4)
    datab = np.empty(y, dtype='int64')
    comm.Recv([datab, MPI.INT], source=0, tag=1)

    # Merge data and datab
    merged = np.sort(np.concatenate((data,datab)), kind='merge')
    # print(data)
    # print(datab)
    # print(merged)
    # tag 5 is length of merged array, tag 6 is the merged array
    comm.send(merged.size, dest=0, tag=5) 
    comm.Send([merged, MPI.INT], dest=0, tag=6)


