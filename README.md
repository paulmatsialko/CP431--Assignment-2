# Assignment 2: Parallel Merging of Two Sorted Arrays

MPI4PY implementation of the parallel merging algorithm for two sorted arrays, for use on the **orca SHARCnet cluster**.

## Algorithm

- **Input:** Two sorted arrays A and B, each of size n.
- **Step 1 – Partition A:** Divide A into r groups of size k = log(n).  
  Group i: A[(i-1)k+1 .. ik] (0-indexed: A[(i-1)*k : i*k], last group to n).
- **Step 2 – Split points in B:** Find r integers j(1)..j(r) using binary search:  
  j(i) = greatest index in B such that A_ik >= B[j(i)].  
  This gives where each group of A “ends” in B.
- **Step 3 – Partition B:** Group iB = B[j(i-1)+1 .. j(i)] (with j(0)=-1, j(r)=n-1).
- **Assignment:** Processor i merges Group i of A with Group i of B. Merging these groups independently gives the final sorted array C.

## Requirements

- Python 3 with **numpy** and **mpi4py**
- On orca: load appropriate modules (e.g. `python/3.10`, `openmpi`) and ensure `mpi4py` is available in that environment

## Usage

- **Command line:**  
  `mpirun -np <P> python3 parallel_merge.py [n]`  
  Default: `n=1_000_000`. Optional argument sets the size of both A and B (each of length n; randomly generated then sorted).

- **Run several tests (Bash):**  
  `./run_tests.sh`  
  Set `MPI_PROCS` if needed (e.g. `MPI_PROCS=8 ./run_tests.sh`).

- **Submit on orca (SLURM):**  
  1. Edit `submit_orca.sbatch`: set `#SBATCH --account=def-USERNAME` to your SHARCNET account.  
  2. Ensure the correct modules are loaded (e.g. `module load python/3.10 openmpi` and mpi4py).  
  3. Run: `sbatch submit_orca.sbatch`

## SHARCNET Etiquette

- Follow the course outline and cluster documentation for job size, time limits, and etiquette.
- Use the assigned cluster (orca) and avoid running large jobs on login nodes; submit via `sbatch` for real runs.

## Files

- `parallel_merge.py` – main MPI code (splitters, scatter of segments, local merge, gather, validation).
- `run_tests.sh` – runs multiple tests with different `(n, m)`.
- `submit_orca.sbatch` – example SLURM script for orca.
- `README.md` – this file.
