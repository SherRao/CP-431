import numpy as np
from mpi4py import MPI

n = 10


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if rank == 0:
    
    a = np.random.randint(0, 5*n, size=n, dtype='i')
    a = np.sort(a)
    b = np.random.randint(0, 5*n, size=n, dtype='i')
    b = np.sort(b)

    #print(a)
    a_s = np.array_split(a, size - 1)
    
    for i in range(1, size) :
        #tag 0 is an A list block
        comm.send( len(a_s[i-1]) , dest=i, tag=3)
        comm.Send([ a_s[i-1] , MPI.INT], dest=i, tag=0)
       

    print("sent")

elif rank >= 1:
    x = comm.recv(source=0, tag=3)
    data = np.empty( x , dtype='i')
    #print(rank, "++")

    comm.Recv([data, MPI.INT], source=0, tag=0)
    #comm.Barrier()

    print(data)
