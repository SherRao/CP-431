import numpy as np
import time
import sys

BIG_N = 100_000_000		# The number of integers
MAX_INT = 10 * BIG_N	# The range in which random ints are generated
PRINT_ARRAY_LIMIT = 20	# Don't print arrays if size exceeds this value


def array_generation():
	sort_time_start = time.time()
	a = np.random.randint(0, MAX_INT, size=BIG_N, dtype='int64')
	a = np.sort(a)
	b = np.random.randint(0, MAX_INT, size=BIG_N, dtype='int64')
	b = np.sort(b)
	sort_time_end = time.time()

	print(f"Time to generate and sort arrays = {sort_time_end - sort_time_start: .4f} seconds")
	print(f"The two generated arrays are of length {BIG_N}.")
	if(BIG_N < PRINT_ARRAY_LIMIT):
		print("The two arrays are:")
		print(f"A: {a}")
		print(f"B: {b}")

	else:
		print("The arrays are too large to print.")

	return a, b

def parallel_merge(a, b):
	merge_start_time = time.time()
	merged = np.sort(np.concatenate((a,b)), kind='merge')
	merge_end_time = time.time()

	print(f'Size of merged array: {sys.getsizeof(merged) / 1_000_000: ,.2f} MB')
	print(f"Time to merge = {merge_end_time - merge_start_time: .4f} seconds")
	if (BIG_N < PRINT_ARRAY_LIMIT):
		print("Merged: ", merged)

	return merged

def main():
	a, b = array_generation()
	merged = parallel_merge(a, b)
	return


if __name__ == "__main__":
	main()
