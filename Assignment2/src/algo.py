import numpy as np
from mpi4py import MPI
import sort

BIG_N = 10000000 # The number of integers
MAX_INT = 5 * BIG_N # The range in which random ints are generated
PRINT_LIMIT = 20 # Don't print arrays if size exceeds this value


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if rank == 0:
    # Generate to randomly sorted lists
    print(f"N = {BIG_N:,} cores={size}")

    sort_time_start = MPI.Wtime()
    a = np.random.randint(0, MAX_INT, size=BIG_N, dtype='i')
    a = np.sort(a)
    b = np.random.randint(0, MAX_INT, size=BIG_N, dtype='i')
    b = np.sort(b)
    sort_time_end = MPI.Wtime()
    print(f"Time to generate and sort arrays = {sort_time_end - sort_time_start: .4f} seconds")

    # a = np.array([2,13,16,17,33,35,41,48,51,52,53], dtype='i')
    # b = np.array([4,21,27,31,31,36,36,41,44,45,46,54], dtype='i')

    # print arrays if they are small
    if (BIG_N < PRINT_LIMIT):
        print("A:      ", a)
        print("B:      ", b)

    # merge_start_time = MPI.Wtime()
    # Split the list into parts based on number of cores
    a_s = np.array_split(a, size - 1)
    # print(a_s)
    
    for i in range(1, size) :
        # tag 0 is an A list block
        comm.send( len(a_s[i-1]) , dest=i, tag=3)
        comm.Send([ a_s[i-1] , MPI.INT], dest=i, tag=0)
    
    # O(n) search for break points in B to create blocks
    # initialize all elements to be length of b, and set first element to be 0
    
    

    breaks = [len(b)]*size 
    breaks[0] = 0
    
    merge_start_time = MPI.Wtime()
    
    b_index, breaks_index = 0, 1# SMALL OPTIMIZATION
    for group in range(len(a_s)-1):
        for b_elem in b[b_index:(b_index+(group))]:
            if b_elem > a_s[group][-1]:
                breaks[breaks_index] = b_index
                breaks_index += 1
                break
            b_index += 1

    merge_end_time = MPI.Wtime()

    breaks[-1] = len(b)
    
    for i in range(1, size):
        # tag 1 is a B list block
        lower, upper = breaks[i-1], breaks[i]
        comm.send(len(b[lower:upper]), dest=i, tag=4)
        comm.Send([b[lower:upper], MPI.INT], dest=i, tag=1)
        # print("sending: ", b[lower:upper], lower, upper)
        

    # print("sent", b, breaks)
    
    # receive merged arrays.
    merged_arrays = [None] * (size-1)
    for i in range(1,size):
        # tag 5 is length of merged array, tag 6 is the merged array
        size = comm.recv(source=i, tag=5) 
        merged = np.empty( size, dtype='i')
        comm.Recv([merged, MPI.INT], source=i, tag=6)
        merged_arrays[i-1] = merged
    
    merged_arrays = np.concatenate(merged_arrays, dtype = 'i')

    # merge_end_time = MPI.Wtime()
    
    
    if (BIG_N < PRINT_LIMIT):
        print("Merged: ", merged_arrays, merged_arrays.shape)
    print(f"Time to parallel merge = {merge_end_time - merge_start_time: .4f} seconds")


elif rank >= 1:
    # Get an A block, first size then numpy array
    x: int = comm.recv(source=0, tag=3)
    data = np.empty( x , dtype='i')
    comm.Recv([data, MPI.INT], source=0, tag=0)
    
    #Get a B block of arbitrary size
    y:int = comm.recv(source=0, tag=4)
    datab = np.empty(y, dtype='i')
    comm.Recv([datab, MPI.INT], source=0, tag=1)

    # Merge data and datab
    #merged = np.sort(np.concatenate((data, datab)))
    
    
    merged = sort.sort(data, datab, x, y)
    # I don't wanna remove this for emotional reasons
    # i: int = 0
    # j: int = 0
    # k: int = 0

    #merged: np.ndarray = np.empty(x+y, dtype='i')
    
    # while i < x and j < y:
    #   if data[i] < datab[j]:
    #     merged[k] = data[i]
    #     i += 1
    #   else:
    #     merged[k] = datab[j]
    #     j += 1
    #   k += 1
    
    # # # add the remaining elements of data or datab to k
    # if (x-i != 0): merged[k:] = data[i:]
    # else: merged[k:] = datab[j:]

    # print(data, " ", datab, " ", rank)
    print(len(data), "<>", len(datab), "<>", len(merged), "<>", rank)

    # tag 5 is length of merged array, tag 6 is the merged array
    #comm.send(merged.size, dest=0, tag=5) 
    comm.send(len(merged), dest=0, tag=5)
    comm.Send([merged, MPI.INT], dest=0, tag=6)


