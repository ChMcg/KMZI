from __future__ import annotations
from bitarray import bitarray
from enum import Enum

from des.des_materials import DES_materials
from des.other import bits_to_raw, chunks, hex_to_raw, xor, shift, permutation, split_halves, bytes_to_str_bitarray, bits_to_hex
from des.other import print_table_of_bits, print_table

from tqdm import tqdm


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
        inner = data[1:-1]
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

    @staticmethod
    def _f(data: str, key: str) -> str:
        if len(data) != 32 or len(key) != 48:
            raise InvalidBlockSizeException()
        tmp = xor(permutation(data, DES_materials.E), key)
        tmp = s_box.apply_to(tmp)
        tmp = permutation(tmp, DES_materials.P)
        return tmp
    
    @staticmethod
    def _generate_keys(key: str) -> list[str]:
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
        # for i, key in enumerate(keys):
        #     print(f"k_{i+1}", key, sep='\t')
        return keys
    
    @staticmethod
    def _encrypt(data: str, key: str) -> str:
        if len(data) != 64 or len(key) != 64:
            raise InvalidBlockSizeException()
        keys = DES._generate_keys(key)
        # print('---- Текст ----')
        # print_table_of_bits(data, 8)
        tmp = permutation(data, DES_materials.IP)
        # print('---- После перестановки ----')
        # print_table_of_bits(tmp, 8)
        left, right = split_halves(tmp)
        # print('---- Левая часть ----')
        # print_table_of_bits(left, 8)
        # print('---- Правая часть ----')
        # print_table_of_bits(right, 8)
        for i in range(15):
            # print(f"---- Раунд {i+1} ----")
            # print(f"A_{i}", left)
            # print(f"B_{i}", right)
            # print(f"K_{i+1}", '=', keys[i])
            # print(f"f = {DES._f(right, keys[i])}")
            # print()
            # print(f"    ", left)
            # print(f"xor ", DES._f(right, keys[i]))
            # print( "is  ", xor(left, DES._f(right, keys[i])))
            left = xor(left, DES._f(right, keys[i]))
            left, right = right, left
        left = xor(left, DES._f(right, keys[16-1]))
        left, right = right, left
        return permutation(left + right, DES_materials.FP)
    
    @staticmethod
    def _decrypt(data: str, key: str) -> str:
        if len(data) != 64 or len(key) != 64:
            raise InvalidBlockSizeException()
        keys = DES._generate_keys(key)
        tmp = permutation(data, DES_materials.IP)
        left, right = split_halves(tmp)
        for i in range(15):
            right = xor(right, DES._f(left, keys[15-i]))
            left, right = right, left
            # print(f"{i+1:2}:", left, right)
        right = xor(right, DES._f(left, keys[0]))
        left, right = right, left
        # print(f"{16}:", left, right)
        return permutation(left + right, DES_materials.FP)

    def _encrypt_str(data: str, key: str) -> str:
        bytes_data = bytes_to_str_bitarray(data.encode(), len(data.encode())*8)
        bytes_key = bytes_to_str_bitarray(key.encode(), 64)
        for chunk in chunks(bytes_data, 64):
            if len(chunk) < 64: 
                chunk += '0' * (64 - len(chunk))
        return ''.join([DES._encrypt(chunk, bytes_key) for chunk in chunks(bytes_data, 64)])
        # return ''.join([DES._encrypt(chunk, bytes_key) for chunk in tqdm(chunks(bytes_data, 64))])

    def _decrypt_str(data: str, key: str) -> str:
        bytes_data = bytes_to_str_bitarray(data.encode(), len(data.encode()))
        bytes_key = bytes_to_str_bitarray(key.encode(), 64)
        return ''.join([DES._decrypt(chunk, bytes_key) for chunk in chunks(bytes_data, 64)])

    def _decrypt_bits(data: str, key: str) -> str:
        bytes_data = data
        bytes_key = bytes_to_str_bitarray(key.encode(), 64)
        return ''.join([DES._decrypt(chunk, bytes_key) for chunk in chunks(bytes_data, 64)]) 

    @staticmethod
    def encrypt(data: str, key: str) -> Data:
        tmp = DES._encrypt_str(data, key)
        return Data(tmp, DataType.Bits)

    @staticmethod
    def decrypt(data: Data, key: str) -> Data:
        return Data(DES._decrypt_bits(data.to_bits(), key), DataType.Bits)


class DataType(Enum):
    Raw     = 0
    Bits    = 1
    Hex     = 2

class Data:
    data: str
    data_type: DataType

    def __init__(self, data: str, data_type: DataType) -> None:
        self.data = data
        self.data_type = data_type
    
    def to_raw(self) -> str:
        if self.data_type == DataType.Bits: return bits_to_raw(self.data)
        if self.data_type == DataType.Raw:  return self.data
        if self.data_type == DataType.Hex:  return hex_to_raw(self.data)
        raise Exception("Unhandled data type" + str(self.data_type))

    def to_hex(self) -> str:
        if self.data_type == DataType.Hex:  return self.data
        if self.data_type == DataType.Bits: return bits_to_hex(self.data)
        raise Exception("Unhandled data type" + str(self.data_type))

    def to_bits(self) -> str:
        if self.data_type == DataType.Bits: return self.data
        raise Exception("Unhandled data type" + str(self.data_type))
        


if __name__ == '__main__':
    des = DES()
    encrypted = des._encrypt_str('Bakhir_Andrey', '736103')
    print(encrypted)
    print(bits_to_hex(encrypted))
    # print(hex_to_raw(bits_to_hex(encrypted)))
    decrypted = des._decrypt_bits(encrypted, '736103')
    print(decrypted)
    print(bits_to_hex(decrypted))
    print(hex_to_raw(bits_to_hex(decrypted)))


    