#!/usr/bin/env python
# encoding: utf-8
# Revisión 2019 (a Python 3 y base64): Pablo Ventura
# Revisión 2014 Carlos Bederián
# Revisión 2011 Nicolás Wolovick
# Copyright 2008-2010 Natalia Bidart y Daniel Moisset
# $Id: server.py 656 2013-03-18 23:49:11Z bc $

import optparse
import socket
import connection
import threading
from constants import *
import sys

class Server(object):
    """
    El servidor, que crea y atiende el socket en la dirección y puerto
    especificados donde se reciben nuevas conexiones de clientes.
    """

    def __init__(self, addr=DEFAULT_ADDR, port=DEFAULT_PORT,
                 directory=DEFAULT_DIR):
        print("Serving %s on %s:%s." % (directory, addr, port))

        self.directory = directory
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (addr, port)
        self.socket.bind(server_address)
        self.semaphore = threading.BoundedSemaphore(value=5)

    def serve(self):
        """
        Loop principal del servidor. Se acepta una conexión a la vez
        y se espera a que concluya antes de seguir.
        """
        self.socket.listen()

        while True:
            print("Waiting for a connection.")
            connection_sock, client_address = self.socket.accept()
            print("Connection from", client_address)
            new_connection = connection.Connection(
                connection_sock, self.directory)
            client_handler = ClientHandler(new_connection, self.semaphore)
            client_handler.start()

    def handle_connection(self, new_connection):
        with self.semaphore:
            new_connection.handle()


class ClientHandler(threading.Thread):
    def __init__(self, connection, semaphore):
        super(ClientHandler, self).__init__()
        self.connection = connection
        self.semaphore = semaphore

    def run(self):
        with self.semaphore:
            self.connection.handle()


def main():
    """Parsea los argumentos y lanza el server"""

    parser = optparse.OptionParser()
    parser.add_option(
        "-p", "--port",
        help="Número de puerto TCP donde escuchar", default=DEFAULT_PORT)
    parser.add_option(
        "-a", "--address",
        help="Dirección donde escuchar", default=DEFAULT_ADDR)
    parser.add_option(
        "-d", "--datadir",
        help="Directorio compartido", default=DEFAULT_DIR)

    options, args = parser.parse_args()
    if len(args) > 0:
        parser.print_help()
        sys.exit(1)
    try:
        port = int(options.port)
    except ValueError:
        sys.stderr.write(
            "Numero de puerto invalido: %s\n" % repr(options.port))
        parser.print_help()
        sys.exit(1)

    server = Server(options.address, port, options.datadir)
    server.serve()


if __name__ == '__main__':
    main()
