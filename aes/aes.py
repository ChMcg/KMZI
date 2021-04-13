from aes.aes_materials import s_box_0, Rcon
from aes.aes_other import setOfFourBytes, Column, Row, Matrix



class s_box():
    box = s_box_0

    @staticmethod
    def apply_to(block: int) -> int:
        _hex = hex(block)[2:]
        if len(_hex) != 2:
            raise Exception()
        a, b = [int(x, 16) for x in _hex]
        return s_box.box[a*16 + b]

        

text = b"bakhir_andrey".ljust(16, b'\x00')[:16]
key  = b"7361_dmitrievich".ljust(16, b'\x00')[:16]
# hex = [hex(x)[2:] for x in text]


def matrix(a: list[str]):    
    for i in range(4):
        print(' '.join([f"{x:0>2}" for x in a[i*4:i*4+4]]))

def raw_matrix(a: bytes):
    matrix([hex(x)[2:] for x in a])

# matrix(hex)
# raw_matrix(text)
# raw_matrix(key)

text = Matrix.from_string('bakhir_andrey')
key = Matrix.from_string('7361_dmitrievich')

print(text)
print(key)

# print(text)
# c = text.columns()
# c[0].rotate(1)
# text.set_columns(c)
# print(text)

# 1'st round
new_state = Matrix.from_string('')
new_state.set_columns([a.xor(b) for a,b in zip(text.columns(), key.columns())])
# print(new_state)

# 1'st subkey
new_state = Matrix.from_string('')
cols = key.columns()
new = cols[3]
new.rotate(1)
new = Column(raw=[s_box.apply_to(x) for x in new.raw])
new = cols[0].xor(new).xor(Rcon[1])
new_state.set_column(0, new)
for i in range(3):
    new = key.columns()[i+1].xor(new_state.columns()[i])
    new_state.set_column(i+1, new)

print(new_state)

# print(Column(raw=[0x2b, 0x7e, 0x15, 0x16]).xor(Column(raw=[0x8a,0x84,0xeb,0x01]).xor(Column(raw=[1,0,0,0]))))


