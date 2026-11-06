"""Послідовний алгоритм (базова лінія для порівняння з PARCS).

Запуск:  python3 serial.py 2000000
Використовує ту саму функцію is_prime, що й воркери в solver.py.
"""
import sys
import time


def is_prime(n):
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


def serial_count(max_range):
    count = 1 if max_range >= 2 else 0  # число 2
    for i in range(3, max_range + 1, 2):
        if is_prime(i):
            count += 1
    return count


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1000000
    t0 = time.time()
    total = serial_count(n)
    elapsed = time.time() - t0
    print("Range: 2..%d" % n)
    print("Total primes: %d" % total)
    print("Serial time (s): %.3f" % elapsed)