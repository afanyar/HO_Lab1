# -*- coding: utf-8 -*-
# NOTE: this file is intentionally pure ASCII so it loads on both Python 2 and Python 3.
from Pyro4 import expose
import time


class Solver:
    """Prime counting on [2, N] for PARCS-Python.

    Input file: a single integer N (upper bound of the range).

    Load distribution: block-cyclic.
    The range is split into blocks of 5000 numbers; block k goes to the
    worker with number (k mod num_workers). Large numbers take longer to
    test, so interleaving blocks balances the load better than giving each
    worker one contiguous chunk. Unlike an element-wise cyclic split
    (3 + 2*rank, step 2*num), blocks never create a "degenerate" worker for
    an odd number of workers (with 3 workers one of them would only get
    multiples of 3 and do almost no work).
    """

    def __init__(self, workers=None, input_file_name=None, output_file_name=None):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        self.workers = workers
        print("Inited")

    # ---------------- master ----------------
    def solve(self):
        print("Job Started")
        n_workers = len(self.workers)
        print("Workers %d" % n_workers)

        max_range = self.read_input()

        start = time.time()

        # map: send (rank, number of workers, N) to every worker
        mapped = []
        for rank in range(n_workers):
            mapped.append(self.workers[rank].count_primes(rank, n_workers, max_range))

        # reduce: collect the results
        results = self.myreduce(mapped)

        elapsed = time.time() - start

        self.write_output(max_range, n_workers, results, elapsed)
        print("Job Finished")

    @staticmethod
    @expose
    def myreduce(mapped):
        # mapped[i].value = [number of primes, worker time in seconds]
        return [m.value for m in mapped]

    # ---------------- worker ----------------
    @staticmethod
    @expose
    def count_primes(rank, num_workers, max_range):
        t0 = time.time()
        chunk = 5000  # block size
        count = 0
        k = rank
        while True:
            lo = 2 + k * chunk
            if lo > max_range:
                break
            hi = min(lo + chunk - 1, max_range)
            if lo <= 2 <= hi:
                count += 1  # the number 2
            x = lo if lo % 2 == 1 else lo + 1
            if x < 3:
                x = 3
            while x <= hi:
                if Solver.is_prime(x):
                    count += 1
                x += 2
            k += num_workers
        return [count, time.time() - t0]

    @staticmethod
    @expose
    def is_prime(n):
        # trial division up to sqrt(n); n is odd, n >= 3
        if n < 2:
            return False
        if n % 2 == 0:
            return n == 2
        d = 3
        while d * d <= n:
            if n % d == 0:
                return False
            d += 2
        return True

    # ---------------- input / output ----------------
    def read_input(self):
        f = open(self.input_file_name, 'r')
        value = None
        for line in f:
            line = line.strip()
            if line:
                value = int(line)
                break
        f.close()
        if value is None or value < 2:
            raise ValueError("Input file must contain an integer N >= 2")
        return value

    def write_output(self, max_range, n_workers, results, elapsed):
        total = sum(r[0] for r in results)
        f = open(self.output_file_name, 'w')
        f.write("Range: 2..%d\n" % max_range)
        f.write("Workers: %d\n" % n_workers)
        f.write("Total primes: %d\n" % total)
        f.write("Parallel time (s): %.3f\n" % elapsed)
        for rank, r in enumerate(results):
            f.write("worker %d: primes=%d, time=%.3f s\n" % (rank, r[0], r[1]))
        f.close()
        print("output done")