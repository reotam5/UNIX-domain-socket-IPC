import argparse
from client_server_utils import (
    SOCKET_ADDRESS_FAMILY,
    SOCKET_KIND,
    SOCKET_BACKLOG,
    try_except_wrapper,
    send_data,
    receive_data,
)
import socket
import os
import errno


class Server:
    def __init__(self, socket_path):
        self.socket_path = socket_path
        self.socket: socket.socket

    @try_except_wrapper("Unnable to unlink a file.")
    def __unlink_if_exists(self):
        try:
            os.unlink(self.socket_path)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise

    def __get_file_permission(self, file_path):
        try:
            return oct(os.stat(file_path).st_mode)[-3:]
        except FileNotFoundError:
            return "File not found"
        except PermissionError:
            return "Permission denied"
        except:
            return "Unknown error while tyring to obtain file permission information"

    @try_except_wrapper("Unnable to create socket.")
    def __create_socket(self):
        self.socket = socket.socket(SOCKET_ADDRESS_FAMILY, SOCKET_KIND)
        if not self.socket:
            raise

    @try_except_wrapper("Unnable to bind socket.")
    def __bind_socket(self):
        self.socket.bind(self.socket_path)

    @try_except_wrapper("Unnable to listen to socket.")
    def __listen_socket(self):
        self.socket.listen(SOCKET_BACKLOG)

    def start(self):
        try:
            self.__unlink_if_exists()
            self.__create_socket()
            self.__bind_socket()
            self.__listen_socket()

            while True:
                connection, _ = self.socket.accept()
                try:
                    data = receive_data(connection)
                    send_data(connection, self.__get_file_permission(data))
                finally:
                    connection.close()

        finally:
            self.socket.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Creates a socket and recieves a file path from client, then responds back with its file permission details."
    )
    parser.add_argument("socket_path", help="The path to bind socket to")
    args = parser.parse_args()

    server = Server(args.socket_path)
    server.start()
