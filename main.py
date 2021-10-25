from rsa.rsa import RSA, Data
from rsa.rsa_other import generate_prime
from tqdm import tqdm


if __name__=='__main__':
    keys = RSA.generate_keys()
    raw = 'Test test test'
    encrypted = RSA.encrypt(raw, keys.public)
    decrypted = RSA.decrypt(encrypted, keys.private)
    print(decrypted.to_raw())

