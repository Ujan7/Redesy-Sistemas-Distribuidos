# encoding: utf-8
# Revisión 2019 (a Python 3 y base64): Pablo Ventura
# Copyright 2014 Carlos Bederián
# $Id: connection.py 455 2011-05-01 00:32:09Z carlos $

import socket
from constants import *
from base64 import b64encode
import os


class Connection(object):
    """
    Conexión punto a punto entre el servidor y un cliente.
    Se encarga de satisfacer los pedidos del cliente hasta
    que termina la conexión.
    """

    def __init__(self, socket, directory):
        self.socket = socket
        self.directory = directory
        self.connection_is_alive = True
        self.server_cache = ""

    def handle(self):
        """
        Atiende eventos de la conexión hasta que termina.
        """
        while self.connection_is_alive:
            try:
                server_response_to_client = self.read_command()
                if "\n" in server_response_to_client:
                    server_response_to_client = self.set_response(BAD_EOL)
                    self.process_server_response(server_response_to_client)
                    self.connection_is_alive = False
                else:
                    if (len(server_response_to_client) > 0):
                        print(f"Request: {server_response_to_client}")
                        self.execute_command(server_response_to_client)
            except Exception:
                server_response = self.set_response(INTERNAL_ERROR)
                self.process_server_response(server_response)
                self.connection_is_alive = False
        self.socket.close()

    def receive_and_add_to_cache(self):
        """
        Recibe datos del cliente y los agrega al cache del server.
        """
        try:
            data = self.socket.recv(4096).decode('ascii')
            self.server_cache += data
        except UnicodeDecodeError:
            server_response = self.set_response(BAD_REQUEST)
            self.process_server_response(server_response)
            self.connection_is_alive = False

    def read_command(self):
        """
        Lee un comando del cliente.
        """
        while EOL not in self.server_cache:
            self.receive_and_add_to_cache()
        if EOL in self.server_cache:
            command, self.server_cache = self.server_cache.split(EOL, 1)
            return command
        else:
            return None

    def execute_command(self, command):
        """
        Ejecuta un comando recibido del cliente.
        """
        command = command.split()
        if command[0] == "get_file_listing":
            if len(command) == 1:
                self.get_file_listing()
            else:
                server_response = self.set_response(INVALID_ARGUMENTS)
                self.process_server_response(server_response)
        elif command[0] == "get_metadata":
            if len(command) == 2:
                self.get_metadata(command[1])
            else:
                server_response = self.set_response(INVALID_ARGUMENTS)
                self.process_server_response(server_response)
        elif command[0] == "get_slice":
            if len(command) == 4 and command[2].isdecimal() and command[3].isdecimal():
                self.get_slice(command[1], int(command[2]), int(command[3]))
            else:
                server_response = self.set_response(INVALID_ARGUMENTS)
                self.process_server_response(server_response)
        elif command[0] == "quit":
            if len(command) == 1:
                self.quit()
            else:
                server_response = self.set_response(INVALID_ARGUMENTS)
                self.process_server_response(server_response)
        else:
            server_response = self.set_response(INVALID_COMMAND)
            self.process_server_response(server_response)

    def process_server_response(self, message, encoding='ascii'):
        """
        Genera un mensaje de respuesta al cliente.
        """
        if encoding == 'base64encode':
            message = b64encode(message)
        elif encoding == 'ascii':
            message += EOL
            message = message.encode('ascii')
        else:
            raise ValueError(
                "Invalid encoding, please use 'ascii' or 'base64encode'")
        try:
            while len(message) > 0:
                bytes_sent = self.socket.send(message)
                if bytes_sent == 0:
                    raise ConnectionError("Connection closed by peer")
                message = message[bytes_sent:]
        except (ConnectionError, socket.error) as e:
            print(f"Error: {e}")

    def set_response(self, code):
        """ 
        Devuelve un string con el código de respuesta.
        """
        if code in error_messages:
            return f"{code} {error_messages[code]}"

    def quit(self):
        """
        Cierra la conexión.
        """
        server_response = self.set_response(CODE_OK)
        self.process_server_response(server_response)
        self.connection_is_alive = False

    def get_file_listing(self):
        """
        Devuelve un string con el listado de archivos en el directorio
        compartido.
        """
        server_response = self.set_response(CODE_OK) + EOL
        files = os.listdir(self.directory)

        for file in files:
            server_response += f"{file} {EOL}"

        self.process_server_response(server_response)

    def file_is_on_path(self, filename):
        """
        Verifica si el archivo es válido.
        """
        return os.path.isfile(os.path.join(self.directory, filename))

    def is_valid_filename(self, filename):
        """
        Verifica si el nombre de archivo es válido.
        """
        return all(char in VALID_CHARS for char in filename)

    def get_metadata(self, filename):
        """ 
        Devuelve una cadena con el tamano del archivo en bytes 
        """
        if not self.is_valid_filename(filename):
            server_response = self.set_response(INVALID_ARGUMENTS) + EOL

        elif not self.file_is_on_path(filename):
            server_response = self.set_response(FILE_NOT_FOUND) + EOL

        else:
            file_size = os.path.getsize(os.path.join(self.directory, filename))
            server_response = self.set_response(CODE_OK) + EOL + str(file_size)

        self.process_server_response(server_response)

    def get_slice(self, filename, offset, size):
        """
        Devuelve un string con los datos del archivo `filename' que
        comienzan en `offset' y tienen longitud `size'.
        """
        if not self.file_is_on_path(filename):
            server_response = self.set_response(FILE_NOT_FOUND)

        elif not self.is_valid_filename(filename):
            server_response = self.set_response(INVALID_ARGUMENTS)

        else:
            file_size = os.path.getsize(os.path.join(self.directory, filename))

            if offset < 0 or offset + size > file_size:
                server_response = self.set_response(BAD_OFFSET)

            else:
                server_response = self.set_response(CODE_OK)
                self.process_server_response(server_response)

                with open(os.path.join(self.directory, filename), 'rb') as file:
                    file.seek(offset)
                    data = file.read(size)
                    self.process_server_response(data, encoding="base64encode")
                server_response = ""
        print(f'server_response {server_response}')
        self.process_server_response(server_response)
