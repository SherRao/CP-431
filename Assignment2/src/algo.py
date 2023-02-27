import numpy as np
from mpi4py import MPI
import sys, gc
import sort

BIG_N = 100_000_000 # The number of integers
MAX_INT = 10 * BIG_N # The range in which random ints are generated
PRINT_LIMIT = 20 # Don't print arrays if size exceeds this value
CHECK_CORRECTNESS = False

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

def simple_merge(arr1, arr2):
    return np.sort(np.concatenate((arr1,arr2)), kind='merge')

if rank == 0:
    # Generate to randomly sorted lists
    print(f"N = {BIG_N:,}")

    sort_time_start = MPI.Wtime()
    a = generate_sorted_randint_array(0, MAX_INT, BIG_N, 'i')
    b = generate_sorted_randint_array(0, MAX_INT, BIG_N, 'i')
    sort_time_end = MPI.Wtime()
    print(f"Time to generate and sort arrays = {sort_time_end - sort_time_start: .4f} seconds")

    # print arrays if they are small
    if (BIG_N < PRINT_LIMIT):
        print("A:      ", a)
        print("B:      ", b)

    # Start merge timer
    merge_start_time = MPI.Wtime()
		
    # Split the list into parts based on number of cores
    a_s = np.array_split(a, size - 1)
    
    for i in range(1, size) :
        # tag 0 is an A list block
        comm.send( len(a_s[i-1]) , dest=i, tag=3)
        comm.Send([ a_s[i-1] , MPI.INT], dest=i, tag=0)
    
    # O(n) search for break points in B to create blocks
    breaks = [0]*size 

    for i, group in enumerate(a_s):
        #b_index = binary_search(b, group[-1], breaks[i])
        b_index = sort.binary_search(b, group[-1], breaks[i])
        breaks[i+1] = b_index

    # Set last element to be the length of the array
    breaks[-1] = len(b)
    #breaks = sort.split(size, b, a_s)

    for i in range(1, size):
        # tag 1 is a B list block
        lower, upper = breaks[i-1], breaks[i]
        comm.send(len(b[lower:upper]), dest=i, tag=4)
        comm.Send([b[lower:upper], MPI.INT], dest=i, tag=1)

    # delete a and b array to save memory and prevent spikes in RAM usage in the next part
    #   Doesn't work as intended :(
    # if (not CHECK_CORRECTNESS):
    #     del a
    #     del b
    #     gc.collect()
    
    # receive merged arrays.
    merged_arrays = [None] * (size-1)
    for i in range(1,size):
        # tag 5 is length of merged array, tag 6 is the merged array
        size = comm.recv(source=i, tag=5) 
        merged = np.empty( size, dtype='i')
        comm.Recv([merged, MPI.INT], source=i, tag=6)
        merged_arrays[i-1] = merged
    
    # concatenate all merged arrays into one
    merged_arrays = np.concatenate(merged_arrays, dtype = 'i')
    print(f'Size of merged array: {sys.getsizeof(merged_arrays)/1_000_000: ,.2f} MB')

    # end merge timer
    merge_end_time = MPI.Wtime()
    
    # Print final results and time
    if (BIG_N < PRINT_LIMIT):
        print("Merged: ", merged_arrays)
    print(f"Time to parallel merge = {merge_end_time - merge_start_time: .4f} seconds")
    
    # Check for correctness
    if (CHECK_CORRECTNESS):
        print("Checking for correctness:", end=" ")
        correct = "Correct" if ((merged_arrays==simple_merge(a,b)).all()) else "Incorrect"
        print(correct)


elif rank >= 1:
    # Get an A block, first size then numpy array
    x: int = comm.recv(source=0, tag=3)
    data = np.empty( x , dtype='i')
    comm.Recv([data, MPI.INT], source=0, tag=0)
    
    #Get a B block of arbitrary size
    y: int = comm.recv(source=0, tag=4)
    datab = np.empty(y, dtype='i')
    comm.Recv([datab, MPI.INT], source=0, tag=1)

    # Merge data and datab
    #merged = simple_merge(data, datab)
    merged = sort.sort(data, datab, x, y)

    # tag 5 is length of merged array, tag 6 is the merged array
    comm.send(merged.size, dest=0, tag=5) 
    comm.Send([merged, MPI.INT], dest=0, tag=6)


