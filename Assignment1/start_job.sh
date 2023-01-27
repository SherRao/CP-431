#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=2
#SBATCH --time=00:01:00
#SBATCH --job-name mpi_job
#SBATCH --output=output/mpi_output_%j.txt
#SBATCH --mail-type=ALL
#SBATCH --mail-user=raox6250@mylaurier.ca

cd $SLURM_SUBMIT_DIR

module load gcc
module load openmpi
module load gmp

mpirun ./main
