#!/bin/bash
# Run parallel merge tests with several array sizes on orca (SHARCnet).
# Use: sbatch run_tests.sh   OR   run interactively: ./run_tests.sh
# Algorithm uses two sorted arrays A and B each of size n.

TESTS="1000000
2000000
500000
16000000"

echo "=== Parallel merge tests (algorithm: k=log(n), r groups) ==="
echo "MPI processes: ${MPI_PROCS:-4}"
echo ""

for n in $TESTS; do
  echo "--- Test: n = $n (|A|=|B|=$n) ---"
  mpirun -np ${MPI_PROCS:-4} python3 parallel_merge.py $n
  echo ""
done

echo "=== Done ==="
