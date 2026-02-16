"""
Parallel merging of two sorted arrays using MPI4PY.
Implements the algorithm from "PARALLEL MERGING ALGORITHM" 
"""

import math
import sys
import time
import numpy as np
from mpi4py import MPI


def find_split_points_in_B(A, B, k, r):
    """
    Find split indices j[0..r] in B.
    j(i) = greatest index in B such that A_ik >= B[j(i)] 
    """
    n = len(B)
    j = np.zeros(r + 1, dtype=np.int64)
    j[0] = -1
    j[r] = n - 1
    for i in range(1, r):
        # Value at end of group i in A (1-based: A_ik -> 0-based A[i*k - 1])
        idx_a = i * k - 1
        if idx_a >= len(A):
            j[i] = n - 1
            continue
        val = A[idx_a]
        # Largest index in B such that B[j] <= val
        pos = np.searchsorted(B, val, side="right") - 1
        j[i] = max(-1, pos)
    return j


def sequential_merge(A, B):
    """Merge two sorted arrays into one (sequential). O(n) time."""
    if len(A) == 0 and len(B) == 0:
        return np.empty(0, dtype=A.dtype if len(A) else B.dtype)
    out = np.empty(len(A) + len(B), dtype=A.dtype)
    i, j, k = 0, 0, 0
    while i < len(A) and j < len(B):
        if A[i] <= B[j]:
            out[k] = A[i]
            i += 1
        else:
            out[k] = B[j]
            j += 1
        k += 1
    out[k : k + len(A) - i] = A[i:]
    out[k + len(A) - i :] = B[j:]
    return out


def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    if rank == 0:
        # Two sorted arrays of the same size n (per document)
        n = 1_000_000
        if len(sys.argv) >= 2:
            n = int(sys.argv[1])
        np.random.seed(42)
        A = np.sort(np.random.randn(n).astype(np.float64))
        B = np.sort(np.random.randn(n).astype(np.float64))
        t0 = time.perf_counter()
    else:
        A = B = None
        n = 0

    n = comm.bcast(n, root=0)
    total = 2 * n

    if n == 0:
        if rank == 0:
            print("Empty arrays.")
        return

    # Step 1: k = log(n), r = number of groups
    k = max(1, int(math.log2(n)))
    r = (n + k - 1) // k  # ceil(n / k)

    if rank == 0:
        # Step 2: Find split points in B
        j = find_split_points_in_B(A, B, k, r)
        # Output offset for each group: group i writes at offset[i]
        offset = np.zeros(r + 1, dtype=np.int64)
        for i in range(r):
            len_a = min((i + 1) * k, n) - i * k
            len_b = j[i + 1] - j[i]  # B[j[i-1]+1 : j[i]+1] has length j[i] - j[i-1]
            offset[i + 1] = offset[i] + len_a + len_b
    else:
        j = np.zeros(r + 1, dtype=np.int64)
        offset = np.zeros(r + 1, dtype=np.int64)

    comm.Bcast(j, root=0)
    comm.Bcast(offset, root=0)

    # Assign groups to processes: process p handles groups [start, end)
    start_group = rank * r // size
    end_group = (rank + 1) * r // size
    my_groups = list(range(start_group, end_group))

    if rank == 0:
        # Send each process (except self) its A segments, B segments, and offsets
        for p in range(1, size):
            sg = p * r // size
            eg = (p + 1) * r // size
            chunks = []
            for i in range(sg, eg):
                a_lo, a_hi = i * k, min((i + 1) * k, n)
                b_lo, b_hi = j[i] + 1, j[i + 1] + 1
                chunks.append((A[a_lo:a_hi].copy(), B[b_lo:b_hi].copy(), offset[i]))
            comm.send(chunks, dest=p, tag=0)
        my_chunks = []
        for i in my_groups:
            a_lo, a_hi = i * k, min((i + 1) * k, n)
            b_lo, b_hi = j[i] + 1, j[i + 1] + 1
            my_chunks.append((A[a_lo:a_hi].copy(), B[b_lo:b_hi].copy(), offset[i]))
    else:
        my_chunks = comm.recv(source=0, tag=0)

    # Each process merges its groups and fills local result (in order)
    local_parts = []
    for (seg_a, seg_b, off) in my_chunks:
        local_parts.append(sequential_merge(seg_a, seg_b))
    if local_parts:
        local_merged = np.concatenate(local_parts)
        my_len = len(local_merged)
    else:
        local_merged = np.empty(0, dtype=np.float64)
        my_len = 0

    # Gather: rank 0 needs to place each process's segment at the correct global offset
    all_lens = comm.gather(my_len, root=0)
    if rank == 0:
        result = np.empty(total, dtype=np.float64)
        # Offsets where each process's output starts (by group assignment)
        process_offset = []
        for p in range(size):
            sg = p * r // size
            process_offset.append(offset[sg] if sg < r else total)
        # Copy my segment
        if my_len > 0:
            result[process_offset[0] : process_offset[0] + my_len] = local_merged
        # Receive from others
        for p in range(1, size):
            if all_lens[p] > 0:
                buf = np.empty(all_lens[p], dtype=np.float64)
                comm.Recv(buf, source=p, tag=1)
                result[process_offset[p] : process_offset[p] + all_lens[p]] = buf
    else:
        if my_len > 0:
            comm.Send(local_merged, dest=0, tag=1)

    if rank == 0:
        elapsed = time.perf_counter() - t0
        sorted_ok = np.all(result[:-1] <= result[1:])
        ref = np.concatenate([A, B])
        ref.sort(kind="mergesort")
        equal = np.allclose(result, ref)
        print(f"n = {n}, k = log(n) = {k}, r = {r} groups, P = {size} processes")
        print(f"Total elements: {total}")
        print(f"Sorted: {sorted_ok}, matches sequential merge: {equal}")
        print(f"Time: {elapsed:.4f} s")
        if not (sorted_ok and equal):
            print("WARNING: validation failed.")
        return result
    return None


if __name__ == "__main__":
    main()
