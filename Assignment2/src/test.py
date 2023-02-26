import sort 
import numpy as np

print(sort.test(5))
c = 0
for i in range(10000000):
    if i % 10:
        c += 1
BIG_N = 10000000  # The number of integers
# MAX_INT = 5 * BIG_N

# a = np.random.randint(0, MAX_INT, size=BIG_N, dtype='i')
# a = np.sort(a)
# b = np.random.randint(0, MAX_INT, size=BIG_N, dtype='i')
# b = np.sort(b)

# merged = np.sort(np.concatenate((a, b)))

