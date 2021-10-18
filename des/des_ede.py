from des import DES, Data


class DES_EDE:

    @staticmethod
    def encrypt(data: str, key: str) -> Data:
        enc1 = DES.encrypt(data, key)
        dec1 = DES.decrypt(enc1, key)
        enc2 = DES.encrypt(dec1.to_raw(), key)
        return enc2

    @staticmethod
    def decrypt(data: Data, key: str) -> Data:
        dec1 = DES.decrypt(data, key)
        enc1 = DES.encrypt(dec1.to_raw(), key)
        dec2 = DES.decrypt(enc1, key)
        return dec2

if __name__ == '__main__':
    key = '123'
    # a = DES_EDE.encrypt('test test test', key)
    # b = DES_EDE.decrypt(a, key)
    # print(b.to_raw())

    with open('a.txt', 'r') as f:
        data = f.read(6* 10* 1024)
        print(len(data))
        DES_EDE.encrypt(data, key)

