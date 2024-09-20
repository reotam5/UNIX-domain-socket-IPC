import re
import argparse
import sys
import socket
from client_server_utils import (
    SOCKET_ADDRESS_FAMILY,
    SOCKET_KIND,
    try_except_wrapper,
    send_data,
    receive_data,
)


class Client:
    def __init__(self, socket_path, request_path):
        self.socket_path = socket_path
        self.request_path = request_path
        self.socket: socket.socket

    def __is_valid_permission_set(self, permissions):
        return bool(re.match(r"^[0-7]{3}", permissions))

    @try_except_wrapper("Unnable to create socket.")
    def __create_socket(self):
        self.socket = socket.socket(SOCKET_ADDRESS_FAMILY, SOCKET_KIND)
        if not self.socket:
            raise

    @try_except_wrapper("Unnable to connect to a socket.")
    def __connect_socket(self):
        self.socket.connect(self.socket_path)

    @try_except_wrapper("Unnable to send data over a socket.")
    def __send_data(self):
        send_data(self.socket, self.request_path)

    @try_except_wrapper("Unnable to receive data from a socket.")
    def __receive_data(self):
        return receive_data(self.socket)

    @try_except_wrapper("Unnable to process response.")
    def __handle_response(self, response_data):
        if self.__is_valid_permission_set(response_data):
            print(
                "Permission details of {file}: {permissions}".format(
                    file=self.request_path, permissions=response_data
                )
            )
        else:
            sys.exit(
                "Server responded with an error: {error}".format(error=response_data)
            )

    def start(self):
        try:
            self.__create_socket()
            self.__connect_socket()
            self.__send_data()
            data = self.__receive_data()
            self.__handle_response(data)
        finally:
            self.socket.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="\
            Connects to a socket at <socket_path>, \
            then sends a request to lookup permission info of <-p>. \
            Then displays the response."
    )
    parser.add_argument("socket_path", help="The socket path to connect to.")
    parser.add_argument(
        "-p",
        "--path",
        required=True,
        help="The file path of a file to lookup permission for.",
    )
    args = parser.parse_args()

    client = Client(args.socket_path, args.path)
    client.start()
