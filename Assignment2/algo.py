import numpy as np
from mpi4py import MPI

n = 11


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if rank == 0:
    # Generate to randomly sorted lists
    a = np.random.randint(0, 5*n, size=n, dtype='i')
    a = np.sort(a)
    b = np.random.randint(0, 5*n, size=n, dtype='i')
    b = np.sort(b)

    # Split the list into parts based on number of cores 
    a_s = np.array_split(a, size - 1)
    
    for i in range(1, size) :
        # tag 0 is an A list block
        comm.send( len(a_s[i-1]) , dest=i, tag=3)
        comm.Send([ a_s[i-1] , MPI.INT], dest=i, tag=0)
    
    # O(n) search for break points in B to create blocks
    space = [0]
    c = 0
    for i in a_s[0:size - 2]:
        for j in b[c:]:
            if j > i[-1]:
                space.append(c)
                break
            c+= 1
    space.append(len(b))

    for i in range(1, size):
        # tag 1 is a B list block
        comm.send(len(b[space[i-1]:space[i]-1]), dest=i, tag=4)
        comm.Send([b[space[i-1]:space[i]-1], MPI.INT], dest=i, tag=1)
        print(i)

    print("sent", b, space)

elif rank >= 1:
    # Get an A block, first size then numpy array
    x = comm.recv(source=0, tag=3)
    data = np.empty( x , dtype='i')
    comm.Recv([data, MPI.INT], source=0, tag=0)
    
    #Get a B block of arbitrary size
    y = comm.recv(source=0, tag=4)
    datab = np.empty(y, dtype='i')
    comm.Recv([datab, MPI.INT], source=0, tag=1)

    print(data, " ", datab, " ", rank)


