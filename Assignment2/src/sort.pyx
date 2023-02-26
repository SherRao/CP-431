import cython
from cpython cimport array
import numpy 
cimport numpy


ctypedef numpy.ndarray DTYPE_t
@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)
def sort(numpy.ndarray[int, ndim=1] data, numpy.ndarray[int, ndim=1] datab, int x, int y):
    cdef int i = 0
    cdef int j = 0
    cdef int k = 0
    
    cdef numpy.ndarray[int, ndim=1] merged = numpy.ndarray(x+y, dtype='i')
    #cdef array.array merged = array.array('i', [])
    
    while i < x and j < y:
        if data[i] < datab[j]:
            merged[k] = data[i]
            i += 1
        else:
            merged[k] = datab[j]
            j += 1
        k += 1

    return merged

def test(x):
    cdef int y = 5

    return x + y 