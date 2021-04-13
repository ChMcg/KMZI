from __future__ import annotations
from pydantic import BaseModel


class setOfFourBytes(BaseModel):
    raw: list[int]

    def rotate_forward(self, offset: int):
        self.raw = self.raw[offset:] + self.raw[:offset]

    def rotate_backward(self, offset: int):
        self.raw = self.raw[-offset:] + self.raw[:-offset]
    
    rotate = rotate_forward
    # rotate = rotate_backward

    def xor(self, other: setOfFourBytes) -> setOfFourBytes:
        return setOfFourBytes(raw=[a^b for a,b in zip(self.raw, other.raw)])

    def __str__(self) -> str:
        return ' '.join([hex(x)[2:] for x in self.raw])


class Row(setOfFourBytes):
    pass

class Column(setOfFourBytes):
    pass

class Matrix(BaseModel):
    raw: list[int]
    text: list[str] = []

    def __init__(self, raw_data: bytes):
        if not len(raw_data) == 16:
            raise Exception()
        super().__init__(
                raw=[x for x in raw_data],
                text=[hex(x)[2:] for x in raw_data]
            )
        
    @staticmethod
    def from_string(data: str) -> Matrix:
        return Matrix(data.encode().ljust(16, b'\x00')[:16])
    
    def __str__(self) -> str:
        ret = ''
        for i in range(4):
            ret += ' '.join([f"{hex(x)[2:]:0>2}" for x in self.raw[i*4:i*4+4]]) + '\n'
        return ret

    # def rows(self) -> list[list[int]]:
    #     return [self.raw[i*4:i*4+4] for i in range(4)]
    
    
    def rows(self) -> list[Row]:
        return [Row(raw=self.raw[i*4:i*4+4]) for i in range(4)]
    
    def columns(self) -> list[Column]:
        return [Column(raw=self.raw[i:16:4]) for i in range(4)]
    
    def set_rows(self, rows: list[Row]):
        new_raw = []
        for row in rows:
            new_raw.extend(row)
        self.raw = new_raw

    def set_columns(self, columns: list[Column]):
        new_raw = [0,] * 16
        for row, column in enumerate(columns):
            for i, item in enumerate(column.raw):
                new_raw[row+i*4] = item
        self.raw = new_raw

    def set_column(self, column: int, column_obj: Column):
        for row, value in enumerate(column_obj.raw):
            self.raw[column+row*4] = value

    def set_row(self, row: int, row_obj: Column):
        for column, value in enumerate(row_obj.raw):
            self.raw[column+row*4] = value
