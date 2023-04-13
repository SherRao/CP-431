<div align="center">
  
# _Parallel Programming_ :hammer:

#### A compilation of all assignments from CP431 - Parallel Programming course, written in C / Python / Cython using MPI on the <a href="https://docs.scinet.utoronto.ca/index.php/Teach" target="_blank" rel="noreferrer">Teach Cluster</a>.
  
 </div>

## Breakdown :pushpin: 
### Assignment 1
- Determines the largest gap between a pair of consecutive prime numbers, up to 1, 000, 000, 000, 000 (one trillion).
#### Usage
> To post a job to the scheduler, use `mpicc` to compile your code to a file called "main".
  ```sh
  mpicc main_no_gmp.c -o main -lgmp -lmpi
  ```
>  Then, simply run the shell script (TIME -> HH:MM:SS)
  ```sh
  sbatch start_job.sh <TIME>
  ```
### Assignment 2
- Implements a parallel merging algorithm to merge two sorted arrays of numbers.


## Useful Commands :pencil:
> Compilation
```sh
mpicc -o <FILE> <file.c>
```
> Run MPI
```sh
mpirun <FILE>
```
> Run NUM copies of the program on set nodes
```sh
mpicc test.c -o test
mpirun -np <NUM> ./test
```
> Use hardware threads as independent CPUs
```sh
mpirun -np <NUM> --use-hwthread-cpus ./test
```
