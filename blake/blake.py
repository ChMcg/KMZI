
import struct
from binascii import hexlify
from enum import Enum
from tqdm import tqdm

class State(Enum):
    Unknown         = 0
    InitialState    = 1
    Updating        = 2
    DigestReady     = 3



def rotate_int(x: int, rotate: int, WORDBITS: int = 32, MASK: int = 0xFFFFFFFF) -> int:
    return (x >> rotate) | ((x << (WORDBITS-rotate)) & MASK)


class Blake(object):

    IV = [
        0x6A09E667, 0xBB67AE85,
        0x3C6EF372, 0xA54FF53A,
        0x510E527F, 0x9B05688C,
        0x1F83D9AB, 0x5BE0CD19,
    ]

    C = [
        0x243F6A88, 0x85A308D3,
        0x13198A2E, 0x03707344,
        0xA4093822, 0x299F31D0,
        0x082EFA98, 0xEC4E6C89,
        0x452821E6, 0x38D01377,
        0xBE5466CF, 0x34E90C6C,
        0xC0AC29B7, 0xC97C50DD,
        0x3F84D5B5, 0xB5470917,
    ]

    SIGMA = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        [14, 10, 4, 8, 9, 15, 13, 6, 1, 12, 0, 2, 11, 7, 5, 3],
        [11, 8, 12, 0, 5, 2, 15, 13, 10, 14, 3, 6, 7, 1, 9, 4],
        [7, 9, 3, 1, 13, 12, 11, 14, 2, 6, 5, 10, 4, 0, 15, 8],
        [9, 0, 5, 7, 2, 4, 10, 15, 14, 1, 11, 12, 6, 8, 3, 13],
        [2, 12, 6, 10, 0, 11, 8, 3, 4, 13, 7, 5, 15, 14, 1, 9],
        [12, 5, 1, 15, 14, 13, 4, 10, 0, 7, 6, 3, 9, 2, 8, 11],
        [13, 11, 7, 14, 12, 1, 3, 9, 5, 0, 15, 4, 8, 6, 2, 10],
        [6, 15, 14, 9, 11, 3, 0, 8, 12, 2, 13, 7, 1, 4, 10, 5],
        [10, 2, 8, 4, 7, 6, 1, 5, 15, 11, 9, 14, 3, 12, 13, 0],
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        [14, 10, 4, 8, 9, 15, 13, 6, 1, 12, 0, 2, 11, 7, 5, 3],
        [11, 8, 12, 0, 5, 2, 15, 13, 10, 14, 3, 6, 7, 1, 9, 4],
        [7, 9, 3, 1, 13, 12, 11, 14, 2, 6, 5, 10, 4, 0, 15, 8],
        [9, 0, 5, 7, 2, 4, 10, 15, 14, 1, 11, 12, 6, 8, 3, 13],
        [2, 12, 6, 10, 0, 11, 8, 3, 4, 13, 7, 5, 15, 14, 1, 9],
        [12, 5, 1, 15, 14, 13, 4, 10, 0, 7, 6, 3, 9, 2, 8, 11],
        [13, 11, 7, 14, 12, 1, 3, 9, 5, 0, 15, 4, 8, 6, 2, 10],
        [6, 15, 14, 9, 11, 3, 0, 8, 12, 2, 13, 7, 1, 4, 10, 5],
        [10, 2, 8, 4, 7, 6, 1, 5, 15, 11, 9, 14, 3, 12, 13, 0],
    ]

    MASK32BITS = 0xFFFFFFFF

    def __init__(self):
        self.h = [0]*8
        self.t = 0
        self.cache = b''
        self.salt = [0]*4
        self.state = State.InitialState
        self.nullt = 0
        self.verbose = False

        self.byte2int = self._fourByte2int
        self.int2byte = self._int2fourByte
        self.MASK = self.MASK32BITS
        self.WORDBYTES = 4
        self.WORDBITS = 32
        self.BLKBYTES = 64
        self.BLKBITS = 512
        self.ROUNDS = 14
        self.h = self.IV[:]

    def set_verbose(self, verbose: bool):
        self.verbose = verbose

    def _compress(self, block):
        byte2int = self.byte2int
        MASK = self.MASK

        m = [
            byte2int(
                block[ i*4 : i*4+4 ]
            )
            for i in range(16)
        ]

        v = [0]*16
        v[0: 8] = [self.h[i] for i in range(8)]
        v[8:16] = [self.C[i] for i in range(8)]
        v[8:12] = [v[8+i] ^ self.salt[i] for i in range(4)]
        if self.nullt == 0:
            v[12] = v[12] ^ (self.t & self.MASK)
            v[13] = v[13] ^ (self.t & self.MASK)
            v[14] = v[14] ^ (self.t >> 32)
            v[15] = v[15] ^ (self.t >> 32)

        def G(a, b, c, d, i):
            j = self.SIGMA[round][i]
            k = self.SIGMA[round][i+1]

            v[a] = ((v[a] + v[b]) + (m[j] ^ self.C[k])) & MASK
            v[d] = rotate_int(v[d] ^ v[a], 16)
            v[c] = (v[c] + v[d]) & MASK
            v[b] = rotate_int(v[b] ^ v[c], 12)

            v[a] = ((v[a] + v[b]) + (m[k] ^ self.C[j])) & MASK
            v[d] = rotate_int(v[d] ^ v[a], 8)
            v[c] = (v[c] + v[d]) & MASK
            v[b] = rotate_int(v[b] ^ v[c], 7)

        for round in range(self.ROUNDS):
            G(0, 4,  8, 12, 0)
            G(1, 5,  9, 13, 2)
            G(2, 6, 10, 14, 4)
            G(3, 7, 11, 15, 6)

            G(0, 5, 10, 15,  8)
            G(1, 6, 11, 12, 10)
            G(2, 7,  8, 13, 12)
            G(3, 4,  9, 14, 14)

        self.h = [
            self.h[i] ^ v[i] ^ v[i+8] ^ self.salt[i & 0x3]
                  for i in range(8)]

    def addsalt(self, salt):
        if self.state != State.InitialState:
            raise Exception(
                    'addsalt() not called after init() and before update()'
                )
        saltsize = self.WORDBYTES * 4
        if len(salt) < saltsize:
            salt = (chr(0)*(saltsize-len(salt)) + salt)
        else:
            salt = salt[-saltsize:]
        self.salt[0] = self.byte2int(salt[  : 4])
        self.salt[1] = self.byte2int(salt[ 4: 8])
        self.salt[2] = self.byte2int(salt[ 8:12])
        self.salt[3] = self.byte2int(salt[12:  ])

    def update(self, data):
        self.state = State.Updating

        BLKBYTES = self.BLKBYTES
        BLKBITS = self.BLKBITS

        datalen = len(data)
        if not datalen:
            return

        if isinstance(data, str):
            data = data.encode('UTF-8')

        left = len(self.cache)
        fill = BLKBYTES - left

        if left and datalen >= fill:
            self.cache = self.cache + data[:fill]
            self.t += BLKBITS
            self._compress(self.cache)
            self.cache = b''
            data = data[fill:]
            datalen -= fill

        if datalen >= BLKBYTES:
            iterator = []
            if self.verbose:
                iterator = tqdm(
                    range(datalen, BLKBYTES, -BLKBYTES), unit_scale=64/1024*8, unit='KB')
            else:
                iterator = range(datalen, BLKBYTES, -BLKBYTES)

            for _ in iterator:
                self.t += BLKBITS
                self._compress(data[:BLKBYTES])
                data = data[BLKBYTES:]
                datalen -= BLKBYTES

        if datalen > 0:
            self.cache = self.cache + data[:datalen]

    def digest(self, data=''):
        if self.state == State.DigestReady:
            return self.hash

        if data:
            self.update(data)

        ZZ = b'\x00'
        ZO = b'\x01'
        OZ = b'\x80'
        OO = b'\x81'
        PADDING = OZ + ZZ*128

        tt = self.t + (len(self.cache) << 3)
        msglen = self._int2eightByte(tt)

        sizewithout = self.BLKBYTES - ((self.WORDBITS // 4)+1)

        if len(self.cache) == sizewithout:
            self.t -= 8
            self.update(OO)
        else:
            if len(self.cache) < sizewithout:
                if len(self.cache) == 0:
                    self.nullt = 1
                self.t -= (sizewithout - len(self.cache)) << 3
                self.update(PADDING[:sizewithout - len(self.cache)])
            else:
                self.t -= (self.BLKBYTES - len(self.cache)) << 3
                self.update(PADDING[:self.BLKBYTES - len(self.cache)])
                self.t -= (sizewithout+1) << 3
                self.update(PADDING[1:sizewithout+1])

                self.nullt = 1

            self.update(ZO)
            self.t -= 8

        self.t -= self.BLKBYTES
        self.update(msglen)

        hashval = []
        for h in self.h:
            hashval.append(self._int2fourByte(h))

        self.hash = b''.join(hashval)[:32]
        self.state = State.DigestReady

        return self.hash

    def hexdigest(self, data=''):
        return hexlify(self.digest(data)).decode('UTF-8')

    def _fourByte2int(self, bytestr):
        return struct.unpack('!L', bytestr)[0]

    def _int2fourByte(self, x):
        return struct.pack('!L', x)

    def _int2eightByte(self, x):
        return struct.pack('!Q', x)
