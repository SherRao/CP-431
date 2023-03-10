import cython
from cpython cimport array
import numpy 
cimport numpy

# Sort custom sort function which compiles to C for optimal performance 
ctypedef numpy.ndarray DTYPE_t
@cython.boundscheck(False)
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


@cython.boundscheck(False) # turn off bounds-checking for entire function
cpdef list split(int size, numpy.ndarray[int, ndim=1] b, a_s):

    cdef list breaks = [0]*size 
    breaks[0] = 0

    cdef int b_index = 0 
    cdef int breaks_index = 1
    cdef int x = len(b)
    cdef int com = 0

    for group in a_s:
        com = group[-1]
        while b_index < x:
            if b[b_index] > com:
                breaks[breaks_index] = b_index
                breaks_index += 1
                break
            b_index += 1
    
    breaks[-1] = len(b)

    return breaks

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef int binary_search(numpy.ndarray[int, ndim=1] arr, int elem, int start):
    cdef int first = start
    cdef int last = len(arr)
    cdef int mid = int((first + last)/2)
    
    while first <= last:
        if (mid == len(arr) or arr[mid] == elem):
            return mid
        elif arr[mid] < elem:
            first = mid + 1
        else:
            last = mid - 1

        mid = int((first + last)/2)

    return mid + 1

def test(x):
    cdef int y = 5

    return x + y 