import sys
import socket

SOCKET_ADDRESS_FAMILY = socket.AF_UNIX
SOCKET_KIND = socket.SOCK_STREAM
SOCKET_BACKLOG = 1
MAX_MESSAGE_SIZE = 1024


def encode(data):
    return data.encode("utf-8")


def decode(data):
    return data.decode("utf-8")


def send_data(connection, data):
    encoded_message = encode(data)
    if len(encoded_message) > MAX_MESSAGE_SIZE:
        raise ValueError("message exceeded max size of {value} bytes.".format(value=MAX_MESSAGE_SIZE))
    connection.send(encoded_message[:MAX_MESSAGE_SIZE])


def receive_data(connection):
    return decode(connection.recv(MAX_MESSAGE_SIZE))


def try_except_wrapper(message):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(e)
                sys.exit(message)

        return wrapper

    return decorator
