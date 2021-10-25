from math import gcd, sqrt
from random import randint

def is_prime(num: int) -> bool:
    if num == 2:
        return True
    if num < 2 or num % 2 == 0:
        return False
    for n in range(3, int(sqrt(num))+2, 2):
        if num % n == 0:
            return False
    return True


def ferma_is_prime(number: int) -> bool:
    if (number == 2): return True
    for _ in range(100):
        a = randint(3, number - 2)
        if gcd(a, number) != 1: return False
        if pow(a, number-1, number) != 1: return False
    return True


def generate_prime(base_length: int = 512) -> int:
    bottom = 1 << base_length
    top = (1 << base_length) ^ ((1 << base_length) - 1)
    tmp_int = randint(bottom, top)
    if ferma_is_prime(tmp_int):
        return tmp_int
    while not ferma_is_prime(tmp_int):
        tmp_int = randint(bottom, top)
        if ferma_is_prime(tmp_int):
            return tmp_int


def extended_gcd(a: int, b: int) -> tuple[int]:
    if a == 0:
        return b, 0, 1
    else:
        gcd, x, y = extended_gcd(b % a, a)
        return gcd, y - (b // a) * x, x
