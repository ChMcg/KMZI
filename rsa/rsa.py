from __future__ import annotations
from bitarray import bitarray
from random import randint, shuffle
from math import gcd
from sympy.ntheory.factor_ import totient
import json

from rsa.rsa_other import is_prime
from rsa.rsa_other import generate_prime
from rsa.rsa_other import extended_gcd


class Data:
    data: tuple[int]

    def __init__(self, data: tuple[int]) -> None:
        self.data = data
    
    def to_raw(self) -> str:
        return ''.join(map(chr, self.data))

    def to_hex(self, indent: int = 2) -> str:
        return json.dumps([f"{x:x}" for x in self.data], indent=indent)

    @staticmethod
    def from_str(data: str) -> Data:
        return Data(tuple(map(ord, data)))


class Key:
    value: int
    module: int

    def __init__(self, value: int, module: int) -> None:
        self.value = value
        self.module = module

class PrivateKey(Key):
    pass

class PublicKey(Key):
    pass


class KeyPair:
    private: Key
    public: Key

    def __init__(self, private: Key, public: Key) -> None:
        self.private = private
        self.public = public

    
class RSA:
    @staticmethod
    def _generate_p_q() -> tuple[int, int]:
        return (generate_prime() for _ in range(2))

    @staticmethod
    def _generate_e(euler: int) -> int:
        while True:
            i = randint(7, euler)
            if (gcd(i, euler) == 1): return i

    @staticmethod
    def _generate_d(euler: int, e: int) -> int:
        _gcd, _, arg = extended_gcd(euler, e)
        if _gcd != 1: raise ValueError('Что-то пошло не так')
        return arg % euler

    @staticmethod
    def generate_keys() -> KeyPair:
        p, q = RSA._generate_p_q(); 
        n = p * q
        euler = (p-1) * (q-1)
        e = RSA._generate_e(euler)
        d = RSA._generate_d(euler, e)

        return KeyPair(
                PrivateKey(d, n),
                PublicKey(e, n)
            )
        
    @staticmethod
    def encrypt(data: Data, key: Key) -> Data:
        if isinstance(data, str): data = Data.from_str(data)
        if not isinstance(data, Data): raise ValueError("Необходимо использовать класс Data")

        e, n = key.value, key.module
        return Data(tuple(pow(x, e, n) for x in data.data))

    @staticmethod
    def decrypt(data: Data, key: Key) -> Data:
        if not isinstance(data, Data): raise ValueError("Необходимо использовать класс Data")

        d, n = key.value, key.module
        return Data(tuple(pow(x, d, n) for x in data.data))

