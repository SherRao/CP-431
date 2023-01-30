# CP 431 - Parallel Programming
All my code for my Parallel Programming class.

## Assignment 1
- To post a job to the scheduler, use `mpicc` to compile your code to a file called "main".
  - `mpicc main_no_gmp.c -o main -lgmp -lmpi`
- Then, simply run `sbatch start_job.sh <TIME>` where time is formatted as HH:mm:ss.

## Useful Commands
`mpicc -o <file> <file.c>`
`mpirun <file>`

`mpicc test.c -o hello`
`mpirun -np 4 ./hello`

`mpirun -np 4 --use-hwthread-cpus ./hello`

