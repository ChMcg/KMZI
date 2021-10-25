from bitarray import bitarray
from bitarray.util import int2ba, ba2int
from math import sqrt
from random import randint
from tqdm import tqdm


def is_prime(num: int) -> bool:
    if num == 2:
        return True
    if num < 2 or num % 2 == 0:
        return False
    for n in range(3, int(sqrt(num))+2, 2):
        if num % n == 0:
            return False
    return True

def generate_prime(base_length: int = 32, rand_range: int = 1 << 32) -> int:
    bottom = 1 << base_length
    top = bottom + rand_range
    tmp_int = randint(bottom, top)
    if is_prime(tmp_int):
        return tmp_int
    while not is_prime(tmp_int):
        tmp_int = randint(bottom, top)
        if is_prime(tmp_int):
            return tmp_int

    # base_number = bitarray(base_length)
    # base_number[0] = 1
    # tmp_rand = int2ba(randint(1, rand_range))
    # tmp = base_number + tmp_rand
    # # tmp_int = int.from_bytes(tmp.tobytes(), 'little')
    # tmp_int = ba2int(tmp)
    # if is_prime(tmp_int): 
    #     return tmp
    # else:
    #     while not is_prime(tmp_int):
    #         tmp_rand = int2ba(randint(1, rand_range))
    #         # tmp_rand = randint(1, rand_range)
    #         tmp = base_number + tmp_rand
    #         # tmp_int = int.from_bytes(tmp.tobytes(), 'little')
    #         tmp_int = ba2int(tmp)
    #         if is_prime(tmp_int): 
    #             return tmp
    # # print(a)


def extended_gcd(a: int, b: int) -> tuple[int]:
    if a == 0:
        return b, 0, 1
    else:
        gcd, x, y = extended_gcd(b % a, a)
        return gcd, y - (b // a) * x, x
