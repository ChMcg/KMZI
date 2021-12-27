from protocol import Address, Client


client = Client(6632)

client.handshake(Address('127.0.0.1', 6631))

while True:
    message = input(">>> ")
    client.send_message(message)
