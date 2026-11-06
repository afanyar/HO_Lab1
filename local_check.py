"""Локальна перевірка коректності БЕЗ PARCS і без хмари.

Імітує роботу 1..4 воркерів (викликає Solver.count_primes напряму),
порівнює суму з решетом Ератосфена та з послідовною версією.

Запуск:  python3 local_check.py 100000
"""
import sys
import time

try:
    import Pyro4  # noqa: F401
except ImportError:
    # заглушка, щоб solver.py імпортувався без встановленого Pyro4
    import types
    stub = types.ModuleType("Pyro4")
    stub.expose = lambda f: f
    sys.modules["Pyro4"] = stub

from solver import Solver
from serial import serial_count


def sieve_count(n):
    if n < 2:
        return 0
    flags = bytearray([1]) * (n + 1)
    flags[0:2] = b"\x00\x00"
    i = 2
    while i * i <= n:
        if flags[i]:
            flags[i * i::i] = bytearray(len(flags[i * i::i]))
        i += 1
    return sum(flags)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100000
    expected = sieve_count(n)
    print("N = %d, eratosthenes sieve: %d primes" % (n, expected))

    t0 = time.time()
    s = serial_count(n)
    print("serial:    %d  (%.3f s)  %s" % (s, time.time() - t0, "OK" if s == expected else "MISMATCH"))

    ok = s == expected
    for w in (1, 2, 3, 4):
        parts = [Solver.count_primes(rank, w, n) for rank in range(w)]
        total = sum(p[0] for p in parts)
        status = "OK" if total == expected else "MISMATCH"
        ok = ok and total == expected
        print("%d workers: %d  per-worker counts %s  %s" % (w, total, [p[0] for p in parts], status))

    print("ALL OK" if ok else "THERE ARE MISMATCHES")


if __name__ == "__main__":
    main()