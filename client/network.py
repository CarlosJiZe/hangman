import socket
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.protocol import *

"""
La clase NetworkClient maneja la conexión TCP con el servidof
Encapsula todo lo del socket pata que gui.py no tenga
que saber nada de TCP, solo tengamos llamadas simples
"""

class NetworkClient:
    def __init__(self,host,port):
        #Host y puerto del servidor
        self.host = host
        self.port = port
        self.socket = None #El socket TCP, se inicializa en connect()

    """
        Crea el socket TCP y conecta al servidor.
        Regresa True si la conexión fue exitosa, False si hubo un error.
        AF_INET = IPv4, SOCK_STREAM = TCP
    """
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host,self.port))
            return True
        except Exception as e:
            print(f"[red] Error al conectar: {e}")
            return False
            
    """
        Manda un mensaje al servidor
        build_message() de protocol.py ya agrega el '\n al final
        encode() convierte el string a bytes para enviar por el socket 
    """
    def send(self, message):
        try:
            self.socket.sendall(message.encode())
            return True
        except Exception as e:
            print(f"[red] Error al mandar mensaje: {e}")
            return False
            
    """
        Espera a recibir un mensaje del servidor
        decode() convierte los bytes recibidos a string
        parse_message() del protocolo parte el mensaje en sus componentes
        Regresa una lista como ["LOGIN_OK"] o ["CORRECT","C_MP_TAD_R_","1"]
        Regresa None si hubo un error al recibir o parsear el mensaje 
    """
    def receive(self):
        try:
            data = b""
            while True:
                chunk = self.socket.recv(1)
                if not chunk or chunk == b"\n":
                    break
                data += chunk
            if not data:
                return None
            return parse_message(data.decode())
        except Exception as e:
            print(f"[red] Error al recibir mensaje: {e}")
            return None
            
    """
        Manda el mensaje de login al servidor
        build_message() construye "LOGIN:usuario:password\n"
        Regresa True si el login fue exitoso, False si hubo un error o el login falló
    """
    def login(self, username, password):
        self.send(build_message(MSG_LOGIN,username,password))
        response = self.receive()

        if response and response[0] == MSG_LOGIN_OK:
            return True
        else:
            return False
            
    """
        El setter manda la palabra a adivianr
        build_message() construye "SET_WORD:palabra\n"
    """
    def send_word(self,word):
        self.send(build_message(MSG_SET_WORD,word.upper()))

    """
        El guesser manda una letra para adivinar
        build_message() construye "GUESS:letra\n"
     """
    def send_guess(self,letter):
        self.send(build_message(MSG_GUESS,letter.upper()))

    """
        Cierra el socket de forma adecuada al terminar
    """
    def disconnect(self):
        try:
            if self.socket:
                self.socket.close()
                self.socket = None
        except Exception as e:
            print(f"[red] Error al desconectar: {e}")