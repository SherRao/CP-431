import cython
from cpython cimport array
import numpy as np


cpdef array.array sort(data: np.ndarray, datab: np.ndarray, x: int, y: int):
    cdef int i = 0
    cdef int j = 0
    cdef int k = 0

    #merged = np.empty(x+y, dtype='i')
    cdef array.array merged = array.array('i', [])
    
    while i < x and j < y:
        if data[i] < datab[j]:
            merged.append(data[i])
            #merged[k] = data[i]
            i += 1
        else:
            merged.append(datab[j])
            #merged[k] = datab[j]
            j += 1
        k += 1

        # # add the remaining elements of data or datab to k
        #if (x-i != 0): merged[k:] = data[i:]
        #else: merged[k:] = datab[j:]

    return merged

def test(x):
    cdef int y = 5

    return x + y 