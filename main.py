from rsa.rsa import RSA, Data
import time


if __name__=='__main__':
    start = time.perf_counter()
    keys = RSA.generate_keys()
    end = time.perf_counter()
    print(f"Key generation time: \t{end - start}")

    raw = 'Test test test'
    
    start = time.perf_counter()
    encrypted = RSA.encrypt(raw, keys.public)
    end = time.perf_counter()
    print(f"Encryption time: \t{end - start}")

    start = time.perf_counter()
    decrypted = RSA.decrypt(encrypted, keys.private)
    end = time.perf_counter()
    print(f"Decryption time: \t{end - start}")

    print(f"Decrypted: {decrypted.to_raw()}")

