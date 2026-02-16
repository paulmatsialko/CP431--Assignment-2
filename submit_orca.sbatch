#!/bin/bash
#SBATCH --account=def-USERNAME
#SBATCH --job-name=parallel_merge
#SBATCH --time=0-00:10:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4
#SBATCH --mem=4G
#SBATCH --output=merge_%j.out
#SBATCH --error=merge_%j.err

# Replace def-USERNAME with your SHARCNET account (e.g. def-jdoe).
# Run on orca: sbatch submit_orca.sbatch

module load python/3.10
module load openmpi
# Or whatever modules provide Python + MPI and mpi4py on orca.

cd $SLURM_SUBMIT_DIR
export MPI_PROCS=$SLURM_NTASKS
./run_tests.sh
