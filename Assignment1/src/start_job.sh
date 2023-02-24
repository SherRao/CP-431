#!/bin/bash
#SBATCH --nodes=4
#SBATCH --ntasks-per-node=8
#SBATCH --time=00:10:00
#SBATCH --job-name mpi_job
#SBATCH --output=output/mpi_output_%j.txt
#SBATCH --mail-type=ALL
#SBATCH --mail-user=raox6250@mylaurier.ca

cd $SLURM_SUBMIT_DIR

module load gcc
module load openmpi
module load gmp

mpirun ./main
