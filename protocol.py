from __future__ import annotations
import socket
import pickle
from socket import AF_INET, SOCK_DGRAM, SOCK_STREAM
from random import randint

# from des.des_ede import DES_EDE as Des
from des.des import DES as Des
from des.des import Data as DesData, DataType as DesDataType
from rsa.rsa import RSA
from rsa.rsa import Data as RsaData
from rsa.rsa import PublicKey, PrivateKey, KeyPair
from blake.blake import Blake


class Address:
    host: str
    port: int
    
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
    
    @staticmethod
    def from_tuple(addr: tuple[str, int]) -> Address:
        host, port = addr
        return Address(host, port)

    def to_native(self) -> tuple[str, int]:
        return (self.host, self.port)


class Message:
    data: DesData
    digest: str
    signature: str

    def __init__(self, data: str, digest: str) -> None:
        self.data = data
        self.digest = digest

    def sign(self, private_key: PrivateKey):
        return RSA.encrypt(self.data, private_key)

    def verify(self, public_key: PublicKey):
        return self.data == RSA.decrypt(RsaData.from_str(self.signature), public_key)


class Client:
    listener: socket.socket
    keypair: KeyPair
    DH_key: int
    client_socket: socket.socket
    client_key: PublicKey
    des_module: Des

    def __init__(self, listener_port: int = 6631) -> None:
        self.listener = socket.socket(AF_INET, SOCK_STREAM)
        self.listener.bind(('0.0.0.0', listener_port))
        self.keypair = RSA.generate_keys()
        self.des_module = Des()

    def handshake(self, addr: Address):
        client = socket.socket()
        client.connect(addr.to_native())
        self.client_socket = client

        client.send(pickle.dumps(self.keypair.public))

        data = client.recv(1024)
        client_key: PublicKey = pickle.loads(data)
        self.client_key = client_key
        
        self.dh_key_exchange_as_initiatior()

    def wait_handshake(self):
        self.listener.listen(1)
        client_socket, addr = self.listener.accept()
        self.client_socket = client_socket
        address = Address.from_tuple(addr)

        data = client_socket.recv(1024)
        client_key: PublicKey = pickle.loads(data)
        self.client_key = client_key

        client_socket.send(pickle.dumps(self.keypair.public))

        self.dh_key_exchange_as_second()

    def dh_key_exchange_as_initiatior(self):
        a = randint(1<<31, 1<<32)
        g, p = 5, randint(1<<31, 1<<32)
        A = pow(g, a, p)
        self.client_socket.send(pickle.dumps((g, p, A)))
        data = self.client_socket.recv(1024)
        B = pickle.loads(data)
        K = pow(B, a, p)
        self.DH_key = K
        print(f"DH: {self.DH_key}")

    def dh_key_exchange_as_second(self):
        b = randint(1<<31, 1<<32)
        data = self.client_socket.recv(1024)
        g, p, A = pickle.loads(data)
        B = pow(g, b, p)
        self.client_socket.send(pickle.dumps(B))
        K = pow(A, b, p)
        self.DH_key = K
        print(f"DH: {self.DH_key}")

    def send_message(self, data: str):
        key = str(self.DH_key)
        encrypted = Des.encrypt(data, key)
        digest = Blake().digest(encrypted.to_raw())
        message = Message(encrypted, digest)
        message.signature = RSA.encrypt(RsaData.from_str(message.data.to_raw()), self.keypair.private)
        self.client_socket.send(pickle.dumps(message))
        print(f'Отправлено сообщение: "{data}"')

    def receive_message(self) -> str:
        key = str(self.DH_key)
        data = self.client_socket.recv(10240)
        message: Message = pickle.loads(data)
        origin = Des.decrypt(message.data, key)
        print(f'Получено сообщение: "{origin.to_raw()}"', end=', ')

        valid = message.data.to_raw() == RSA.decrypt(message.signature, self.client_key).to_raw()

        if valid: print("подпись верна")        
        else: print("подпись не верна")
