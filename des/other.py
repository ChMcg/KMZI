from bitarray import bitarray

def chunks(src: str, length: int) -> list[str]:
    n = length
    ret = [src[i:i+n] for i in range(0, len(src), n)]
    for i, chunk in enumerate(ret):
        if len(chunk) < length:
            ret[i] += '0' * (length - len(chunk))
    return ret

def xor(a: str, b: str) -> str:
    def _xor(a: str, b: str) -> str:
        return '1' if a != b else '0'
    
    if len(a) != len(b):
        raise Exception('Lengths not match')
    res = [_xor(x,y) for x,y in zip(a,b)]
    return ''.join(res)

def shift(src: str, value: int) -> str:
    return src[value:] + src[:value]

def permutation(src: str, table: list[int]) -> str:
    if len(src) < max(table): 
        raise OverflowError()
    return ''.join([src[x-1] for x in table])

def split_halves(data: str) -> tuple[str, str]:
    if len(data) % 2 != 0:
        raise Exception()
    n = len(data) // 2
    return (data[:n], data[-n:])

def bytes_to_str_bitarray(src: bytes, length: int) -> str:
    x = bitarray()
    x.frombytes(src)
    ret = x.to01()[0:length]
    if len(ret) < length:
        ret = '0'*(length-len(ret)) + ret
    return ret

def bits_to_hex(bits: str) -> str:
    return ' '.join([hex(eval(f"0b{x}"))[2:] for x in chunks(bits, 8)])

def hex_to_raw(hex: str) -> str:
    return ''.join([chr(eval(f"0x{x}")) for x in hex.split(' ')])

def print_table_of_bits(data: str, rows: int) -> None:
    for i, item in enumerate(data):
        if (i+1) % rows == 0:
            print(f"{item}\n", sep='', end='')
        else:
            print(f"{item} ", sep='', end='')
    print()

def print_table(data: list[str], rows: int) -> None:
    for i, item in enumerate(data):
        if (i+1) % rows == 0:
            print(f"{item}\n", sep='')
        else:
            print(f"{item}\t", sep='')
