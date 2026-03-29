import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.protocol import *
from gui import HangmanGUI

"""
Entry point del cliente Hangman
Recibe el host y puerto como argumentos de línea de comandos
y arranca la interfaz gráfica.

Uso:
    python3 main.py                        → conecta a localhost:5001 (default)
    python3 main.py 192.168.1.5            → conecta a esa IP en puerto 5001
    python3 main.py 192.168.1.5 5001       → conecta a esa IP y puerto
"""

def main():
    # Leemos host y puerto de los argumentos
    # Si no se pasan, usamos localhost y el puerto del protocolo
    host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else PORT

    print(f"Conectando a {host}:{port}...")

    # Creamos y arrancamos la GUI
    app = HangmanGUI(host, port)
    app.run()

if __name__ == "__main__":
    main()