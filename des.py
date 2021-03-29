from bitarray import bitarray
from des_materials import DES_materials
from other import chunks, hex_to_raw, xor, shift, permutation, split_halves, bytes_to_str_bitarray, bits_to_hex
from other import print_table_of_bits, print_table


class InvalidBlockSizeException(BaseException):
    pass

class s_box:
    blocks = dict(zip(
        range(8),
        [
            DES_materials.s_box_1,
            DES_materials.s_box_2,
            DES_materials.s_box_3,
            DES_materials.s_box_4,
            DES_materials.s_box_5,
            DES_materials.s_box_6,
            DES_materials.s_box_7,
            DES_materials.s_box_8
        ]
    ))
    
    @staticmethod
    def _apply_box(box_number: int, data: str) -> str:
        if len(data) != 6:
            raise InvalidBlockSizeException()
        outer = data[1] + data[-1]
        inner = data[2:-2]
        row = eval(f"0b{outer}")
        column = eval(f"0b{inner}")
        n = 16*row + column
        number = s_box.blocks[box_number][n]
        return f"{number:04b}"

    @staticmethod
    def apply_to(block: str) -> str:
        if len(block) != 48:
            raise InvalidBlockSizeException()
        ret = ""
        for i, bits in enumerate(chunks(block, 6)):
            ret += s_box._apply_box(i, bits)
        return ret


class DES:
    def __init__(self):
        pass
    
    def _f(self, data: str, key: str) -> str:
        if len(data) != 32 or len(key) != 48:
            raise InvalidBlockSizeException()
        tmp = xor(permutation(data, DES_materials.E), key)
        tmp = s_box.apply_to(tmp)
        tmp = permutation(tmp, DES_materials.P)
        return tmp
    
    def _generate_keys(self, key: str) -> list[str]:
        if len(key) != 64:
            raise InvalidBlockSizeException()
        keys = []
        left  = permutation(key, DES_materials.PC_1_left) 
        right = permutation(key, DES_materials.PC_1_right)
        for i in range(16):
            left  = shift(left, DES_materials.rotation[i])
            right = shift(right, DES_materials.rotation[i])
            keys.append(permutation(left + right, DES_materials.PC_2))
        # print('---- Ключи ----')
        # for key in keys:
        #     print_table_of_bits(key, 8)
        return keys
    
    def encrypt(self, data: str, key: str) -> str:
        if len(data) != 64 or len(key) != 64:
            raise InvalidBlockSizeException()
        keys = self._generate_keys(key)
        # print('---- Текст ----')
        # print_table_of_bits(data, 8)
        tmp = permutation(data, DES_materials.IP)
        # print('---- После перестановки ----')
        # print_table_of_bits(tmp, 8)
        left, right = split_halves(tmp)
        for i in range(16):
            tmp = right
            right = xor(left, self._f(right, keys[i]))
            left, right = tmp, left
        left, right = right, left
        return permutation(left + right, DES_materials.FP)
    
    def decrypt(self, data: str, key: str) -> str:
        if len(data) != 64 or len(key) != 64:
            raise InvalidBlockSizeException()
        keys = self._generate_keys(key)
        tmp = permutation(data, DES_materials.IP)
        left, right = split_halves(tmp)
        for i in range(16):
            tmp = right
            right = xor(left, self._f(right, keys[i]))
            left, right = tmp, left
        left, right = right, left
        return permutation(left + right, DES_materials.FP)

    def encrypt_str(self, data: str, key: str) -> str:
        bytes_data = bytes_to_str_bitarray(data.encode(), len(data.encode())*8)
        bytes_key = bytes_to_str_bitarray(key.encode(), 64)
        for chunk in chunks(bytes_data, 64):
            if len(chunk) < 64: 
                chunk += '0' * (64 - len(chunk))
            
        return ''.join([self.encrypt(chunk, bytes_key) for chunk in chunks(bytes_data, 64)])

    def decrypt_str(self, data: str, key: str) -> str:
        bytes_data = bytes_to_str_bitarray(data.encode(), len(data.encode()))
        bytes_key = bytes_to_str_bitarray(key.encode(), 64)
        return ''.join([self.decrypt(chunk, bytes_key) for chunk in chunks(bytes_data, 64)])

    def decrypt_bits(self, data: str, key: str) -> str:
        bytes_data = data
        bytes_key = bytes_to_str_bitarray(key.encode(), 64)
        return ''.join([self.decrypt(chunk, bytes_key) for chunk in chunks(bytes_data, 64)]) 



if __name__ == '__main__':
    des = DES()
    encrypted = des.encrypt_str('bakhir_andrey', '736103')
    print(encrypted)
    print(bits_to_hex(encrypted))
    # print(hex_to_raw(bits_to_hex(encrypted)))
    decrypted = des.decrypt_bits(encrypted, '736103')
    print(decrypted)
    print(bits_to_hex(decrypted))
    print(hex_to_raw(bits_to_hex(decrypted)))


    