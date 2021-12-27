from protocol import Client

client = Client(6631)

client.wait_handshake()

while True:
    client.receive_message()

