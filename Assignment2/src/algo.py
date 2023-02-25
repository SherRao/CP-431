import numpy as np
from mpi4py import MPI

n = 1000000


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if rank == 0:
    # Generate to randomly sorted lists
    a = np.random.randint(0, 5*n, size=n, dtype='i')
    a = np.sort(a)
    b = np.random.randint(0, 5*n, size=n, dtype='i')
    b = np.sort(b)

    # a = np.array([8,11,19,30,34,34,37,38,42,43,53], dtype='i')
    # b = np.array([3,4,7,10,17,26,28,32,35,42,44], dtype='i')

    # print(a)
    # print(b)

    # Split the list into parts based on number of cores 
    a_s = np.array_split(a, size - 1)
    
    for i in range(1, size) :
        # tag 0 is an A list block
        comm.send( len(a_s[i-1]) , dest=i, tag=3)
        comm.Send([ a_s[i-1] , MPI.INT], dest=i, tag=0)
    
    # O(n) search for break points in B to create blocks
    space = [0]
    c = 0

    for i in a_s:
        for j in b[c:]:
            if j > i[-1]:
                space.append(c)
                break
            c+= 1
    space.append(len(b))

    for i in range(1, size):
        # tag 1 is a B list block
        comm.send(len(b[space[i-1]:space[i]]), dest=i, tag=4)
        comm.Send([b[space[i-1]:space[i]], MPI.INT], dest=i, tag=1)

    # print("sent", b, space)
    
    # receive merged arrays.
    merged_arrays = [None] * (size-1)
    for i in range(1,size):
        # tag 5 is length of merged array, tag 6 is the merged array
        size = comm.recv(source=i, tag=5) 
        merged = np.empty( size, dtype='i')
        comm.Recv([merged, MPI.INT], source=i, tag=6)
        merged_arrays[i-1] = merged
    
    merged_arrays = np.concatenate(merged_arrays, dtype = 'i')
    # print(merged_arrays)
    print("Done")


elif rank >= 1:
    # Get an A block, first size then numpy array
    x = comm.recv(source=0, tag=3)
    data = np.empty( x , dtype='i')
    comm.Recv([data, MPI.INT], source=0, tag=0)
    
    #Get a B block of arbitrary size
    y = comm.recv(source=0, tag=4)
    datab = np.empty(y, dtype='i')
    comm.Recv([datab, MPI.INT], source=0, tag=1)

    # Merge data and datab
    i=j=k=0
    merged = np.empty(x+y, dtype='i')
    
    while i < x and j < y:
      if data[i] < datab[j]:
        merged[k] = data[i]
        i += 1
      else:
        merged[k] = datab[j]
        j += 1
      k += 1

    merged[k:] = data[i:]

    # print(data, " ", datab, " ", rank)
    # print(merged)

    # tag 5 is length of merged array, tag 6 is the merged array
    comm.send(merged.size, dest=0, tag=5) 
    comm.Send([merged, MPI.INT], dest=0, tag=6)


