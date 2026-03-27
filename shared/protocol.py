"""
Protocolo de comunicación entre el cliente y el servidor
Es lo mismo que el protocolo.h pero para clientes en Python
Todos los mensajes son strings que terminan en '\n'
"""

#Puerto donde corre el servidor (Debe ser el mismo que protocol.h)
PORT = 10820

#Tamaño de buffer al leer mensajes del socket
BUFFER_SIZE = 256

"""
MENSAJES DEL CLIENTE AL SERVIDOR
"""

MSG_LOGIN = "LOGIN" #"LOGIN:usuario:contraseña\n"
MSG_SET_WORD = "SET_WORD" #"SET_WORD:computadora\n" 
MSG_GUESS = "GUESS" #"GUESS:A\n"

"""
MENSAJES DEL SERVIDOR AL CLIENTE
"""

MSG_LOGIN_OK = "LOGIN_OK" #"LOGIN_OK\n"
MSG_LOGIN_FAIL = "LOGIN_FAIL" #"LOGIN_FAIL\n"
MSG_ROLE = "ROLE" #"ROLE:SETTER\n" o "ROLE:GUESSER\n"
MSG_BOARD = "BOARD" # "BOARD:C_MP_TAD_R_\n"
MSG_CORRECT = "CORRECT" # "CORRECT:C_MP_TAD_R_:3\n"
MSG_WRONG = "WRONG" # "WRONG:C_MP_TAD_R_:3\n"
MSG_WIN = "WIN" # "WIN:COMPUTADORA\n"
MSG_LOSE = "LOSE" # "LOSE:COMPUTADORA\n"
MSG_WAIT = "WAIT" # "WAIT\n"
MSG_OPPONENT_LEFT = "OPPONENT_LEFT" # el otro jugador se fue
MSG_ROOM_FULL = "ROOM_FULL" # el servidor no puede aceptar más jugadores
MSG_ERROR = "ERROR" # el servidor informa sobre un error en la validación de la palabra

"""
ROLES
"""

ROLE_SETTER = "SETTER" # El jugador que elige la palabra y espera a que el otro adivine
ROLE_GUESSER = "GUESSER" # El jugador que adivina la palabra del otro

"""
CONSTANTES DEL JUEGO
"""

MAX_ATTEMPTS = 6 # Número máximo de intentos fallidos antes de perder
MAX_PLAYERS = 2 # Número máximo de jugadores en una sala

"""
FUNCIONES AUXILIARES
"""

def build_message(*parts):
    #Construye un mensaje uniendo las parte con ':' y añade '\n'
    #Ejemplo: build_message("LOGIN", "carlos", "1234") que se convierte en "LOGIN:carlos:1234\n"
    return ":".join(parts) + "\n"

def parse_message(raw):
    #Recibe un mensaje crudo y lo parte en sus componentes
    #Ejemplo: parse_message("CORRECT:C_MP_TAD_R_:3\n") → ["CORRECT", "C_MP_TAD_R_", "3"]
    #Siempre quita el '\n' del final antes de partir
    return raw.strip().split(":")

def is_valid_letter(c):
    #Verifica que el caracter sea una letra valida A-Z o a-z
    #Rechaza caracteres especiales, números o espacios
    #No se pueden mandar acentos ni ñ
    #Ejemplo: is_valid_letter("A"): True
    #Ejemplo: is_valid_letter("1"): False
    return c.isalpha() and c.isascii()

def is_valid_word(word):
    #Verifica que la palabra sea valida: solo letras, sin espacios, sin acentos ni ñ
    #Ejemplo: is_valid_word("computer"): True
    #Ejemplo: is_valid_word("año"): False
    return len(word)>0 and all(is_valid_letter(c) for c in word)