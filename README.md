# Assignment 2: Parallel Merging of Two Sorted Arrays

MPI4PY implementation of the parallel merging algorithm for two sorted arrays, for use on the **SHARCnet cluster**.

## Algorithm

- **Input:** Two sorted arrays A and B, each of size n.
- **Step 1 – Partition A:** Divide A into r groups of size k = log(n).  
  Group i: A[(i-1)k+1 .. ik] (0-indexed: A[(i-1)*k : i*k], last group to n).
- **Step 2 – Split points in B:** Find r integers j(1)..j(r) using binary search:  
  j(i) = greatest index in B such that A_ik >= B[j(i)].  
  This gives where each group of A “ends” in B.
- **Step 3 – Partition B:** Group iB = B[j(i-1)+1 .. j(i)] (with j(0)=-1, j(r)=n-1).

## Usage

- **Command line:**  
  `mpirun -np <P> python3 parallel_merge.py [n]`  
  Default: `n=1_000_000`. Optional argument sets the size of both A and B (each of length n; randomly generated then sorted).
  
## Files

- `parallel_merge.py` – main MPI code (splitters, scatter of segments, local merge, gather, validation).
- `README.md` – this file.
