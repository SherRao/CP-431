import numpy as np
import time

BIG_N = 100_000_000 # The number of integers
MAX_INT = 10 * BIG_N # The range in which random ints are generated
PRINT_LIMIT = 20 # Don't print arrays if size exceeds this value

print(f"N = {BIG_N:,}")

sort_time_start = time.time()
a = np.random.randint(0, MAX_INT, size=BIG_N, dtype='int64')
a = np.sort(a)
b = np.random.randint(0, MAX_INT, size=BIG_N, dtype='int64')
b = np.sort(b)
sort_time_end = time.time()

print(f"Time to generate and sort arrays = {sort_time_end - sort_time_start: .4f} seconds")
if (BIG_N < PRINT_LIMIT):
	print("A:      ", a)
	print("B:      ", b)

merge_start_time = time.time()

c = np.sort(np.concatenate((a,b)), kind='merge')

merge_end_time = time.time()

if (BIG_N < PRINT_LIMIT):
		print("Merged: ", c)
print(f"Time to merge = {merge_end_time - merge_start_time: .4f} seconds")