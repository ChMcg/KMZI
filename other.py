from bitarray import bitarray

def chunks(src: str, length: int) -> list[str]:
    n = length
    return [src[i:i+n] for i in range(0, len(src), n)]

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