from bitarray import bitarray
from des_materials import DES_materials
from other import chunks, xor, shift, permutation, split_halves, bytes_to_str_bitarray, bits_to_hex

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
        return keys
    
    def encrypt(self, data: str, key: str) -> str:
        if len(data) != 64 or len(key) != 64:
            raise InvalidBlockSizeException()
        keys = self._generate_keys(key)
        tmp = permutation(data, DES_materials.IP)
        left, right = split_halves(tmp)
        for i in range(16):
            left = xor(left, self._f(right, keys[i]))
            left, right = right, left
        return permutation(left + right, DES_materials.FP)
        


plaintext_str = b"bakhir_andrey"
key_str = b"736103"


if __name__ == '__main__':
    plaintext = bytes_to_str_bitarray(plaintext_str, 64)
    # key = bytes_to_str_bitarray(key_str, 56)
    key = bytes_to_str_bitarray(key_str, 64)
    print(plaintext, len(plaintext), bits_to_hex(plaintext))
    print(key, len(key), bits_to_hex(key))
    encrypted = DES().encrypt(plaintext, key)
    print(encrypted)
    print(bits_to_hex(encrypted))

    