from random import randint
from rsa.rsa import RSA, Data
from blake.blake import Blake
from protocol import Client, Address
import time


def rsa_test():
    start = time.perf_counter()
    keys = RSA.generate_keys()
    end = time.perf_counter()
    print(f"Key generation time: \t{end - start}")

    raw = 'Test test test'
    print('Encrypting:', raw)

    start = time.perf_counter()
    encrypted = RSA.encrypt(raw, keys.public)
    end = time.perf_counter()
    print(f"Encryption time: \t{end - start}")

    print('Encrypted:', encrypted.to_hex())

    start = time.perf_counter()
    decrypted = RSA.decrypt(encrypted, keys.private)
    end = time.perf_counter()
    print(f"Decryption time: \t{end - start}")

    print(f"Decrypted: {decrypted.to_raw()}")


def blake_test():
    blake = Blake()
    data = b''
    with open('/etc/passwd', 'rb') as f:
        data = f.read()
    digest = blake.hexdigest(data)
    print(digest)

def protocol_test():
    port = randint(5000, 5099)
    print(f"port: {port}")
    client = Client(port)
    client.wait_handshake()
    client.receive_message()
        

if __name__ == '__main__':
    # rsa_test()
    # blake_test()
    protocol_test()
