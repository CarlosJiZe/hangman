import tkinter as tk
from tkinter import messagebox
import threading
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.protocol import *
from network import NetworkClient

"""
 Creamos la interfaz gráfica del cliente Hangman
 Usa tkinter para mostrar las pantallas del juego.
 Cada pantalla es un Frame que se muestra/oculta según
 el estado del juego.
"""

# Colores de la interfaz
BG_COLOR     = "#1a1a2e"  # fondo oscuro azul
CARD_COLOR   = "#16213e"  # fondo de tarjetas
ACCENT_COLOR = "#e94560"  # rojo acento
TEXT_COLOR   = "#eaeaea"  # texto claro
SUBTLE_COLOR = "#a0a0b0"  # texto secundario
GREEN_COLOR  = "#4ecca3"  # verde para aciertos
RED_COLOR    = "#e94560"  # rojo para errores
DARK_COLOR   = "#1a1a2e"  # fondo oscuro para botones en ventanas blancas

def make_button(parent, text, command, bg, fg, font_size=12, bold=False, padx=20, pady=8, width=None):
    """
    Crea un botón usando Label + Frame para forzar colores en macOS.
    tkinter en macOS ignora los colores de tk.Button, por eso usamos
    un Label dentro de un Frame de color para simular el botón.
    """
    weight = "bold" if bold else "normal"
    container = tk.Frame(parent, bg=bg, cursor="hand2")
    label = tk.Label(
        container,
        text=text,
        bg=bg,
        fg=fg,
        font=("Helvetica", font_size, weight),
        padx=padx,
        pady=pady,
    )
    if width:
        label.config(width=width)
    label.pack()

    # Hover effect — aclara un poco el fondo al pasar el mouse
    def on_enter(e):
        label.config(bg=_lighten(bg))
        container.config(bg=_lighten(bg))
    def on_leave(e):
        label.config(bg=bg)
        container.config(bg=bg)
    def on_click(e):
        command()

    label.bind("<Enter>", on_enter)
    label.bind("<Leave>", on_leave)
    label.bind("<Button-1>", on_click)
    container.bind("<Enter>", on_enter)
    container.bind("<Leave>", on_leave)
    container.bind("<Button-1>", on_click)

    return container

def _lighten(hex_color):
    """Aclara un color hex un poco para el hover"""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    r = min(255, r + 30)
    g = min(255, g + 30)
    b = min(255, b + 30)
    return f'#{r:02x}{g:02x}{b:02x}'


class HangmanGUI:
    def __init__(self, host, port):
        # Creamos la ventana principal
        self.root = tk.Tk()
        self.root.title("Hangman — Cómputo Distribuido")
        self.root.geometry("600x700")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        # Cliente de red
        self.net = NetworkClient(host, port)

        # Estado del juego
        self.role = None # "SETTER" o "GUESSER"
        self.wrong_attempts = 0
        self.board = ""

        # Frame actual visible
        self.current_frame = None
        self.waiting_message = None # Label del mensaje de espera

        # Mostramos la pantalla de login
        self.show_login()

    """ 
    UTILIDADES
    """ 

    def clear_frame(self):
        """Destruye el frame actual para mostrar uno nuevo"""
        if self.current_frame:
            self.current_frame.destroy()

    def make_frame(self):
        """Crea un frame nuevo con el color de fondo"""
        frame = tk.Frame(self.root, bg=BG_COLOR)
        frame.pack(fill="both", expand=True)
        self.current_frame = frame
        return frame

    def add_nav_buttons(self, parent):
        """Agrega los botones Cómo jugar y Acerca de en la esquina superior derecha"""
        make_button(parent, "Cómo jugar", self.show_how_to_play,
                    bg=CARD_COLOR, fg=TEXT_COLOR, font_size=10, padx=10, pady=5
                    ).place(relx=1.0, x=-115, y=8, anchor="ne")

        make_button(parent, "Acerca de", self.show_about,
                    bg=CARD_COLOR, fg=TEXT_COLOR, font_size=10, padx=10, pady=5
                    ).place(relx=1.0, x=-10, y=8, anchor="ne")

    """ 
    PANTALLA 1 — LOGIN
    """ 

    def show_login(self):
        """Pantalla de login — pide usuario y contraseña"""
        self.clear_frame()
        frame = self.make_frame()

        # Título
        tk.Label(frame, text="HANGMAN", font=("Helvetica", 48, "bold"),
                 bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=(60, 5))
        tk.Label(frame, text="Cómputo Distribuido", font=("Helvetica", 14),
                 bg=BG_COLOR, fg=SUBTLE_COLOR).pack(pady=(0, 40))

        # Card de login
        card = tk.Frame(frame, bg=CARD_COLOR, padx=40, pady=30)
        card.pack(padx=60)

        tk.Label(card, text="Iniciar Sesión", font=("Helvetica", 18, "bold"),
                 bg=CARD_COLOR, fg=TEXT_COLOR).pack(pady=(0, 20))

        # Campo usuario
        tk.Label(card, text="Usuario", font=("Helvetica", 12),
                 bg=CARD_COLOR, fg=SUBTLE_COLOR).pack(anchor="w")
        self.username_entry = tk.Entry(card, font=("Helvetica", 13),
                                       bg="#0f3460", fg=TEXT_COLOR,
                                       insertbackground=TEXT_COLOR,
                                       relief="flat", width=25)
        self.username_entry.pack(pady=(2, 15), ipady=8)

        # Campo contraseña
        tk.Label(card, text="Contraseña", font=("Helvetica", 12),
                 bg=CARD_COLOR, fg=SUBTLE_COLOR).pack(anchor="w")
        self.password_entry = tk.Entry(card, font=("Helvetica", 13),
                                       bg="#0f3460", fg=TEXT_COLOR,
                                       insertbackground=TEXT_COLOR,
                                       show="*", relief="flat", width=25)
        self.password_entry.pack(pady=(2, 25), ipady=8)

        # Mensaje de error (inicialmente vacío)
        self.login_error = tk.Label(card, text="", font=("Helvetica", 11),
                                     bg=CARD_COLOR, fg=RED_COLOR)
        self.login_error.pack(pady=(0, 10))

        # Botón conectar
        make_button(card, "Conectar", self.do_login,
                    bg=ACCENT_COLOR, fg="white",
                    font_size=13, bold=True, padx=40, pady=10, width=20).pack()

        # Enter también hace login
        self.password_entry.bind("<Return>", lambda e: self.do_login())
        self.username_entry.focus()

        self.add_nav_buttons(frame)

    def do_login(self):
        """Conecta al servidor y hace login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self.login_error.config(text="Por favor llena todos los campos")
            return

        # Conectamos al servidor
        if not self.net.connect():
            self.login_error.config(text="No se pudo conectar al servidor")
            return

        # Mandamos el login
        if not self.net.login(username, password):
            self.login_error.config(text="Usuario o contraseña incorrectos")
            self.net.disconnect()
            return

        self.username = username

        # Login exitoso — escuchamos el rol en un hilo separado
        # para no bloquear la interfaz gráfica
        threading.Thread(target=self.wait_for_role, daemon=True).start()

    def wait_for_role(self):
        """Espera el mensaje ROLE del servidor en un hilo separado"""
        response = self.net.receive()
        if not response:
            self.root.after(0, lambda: self.login_error.config(
                text="Error al recibir rol del servidor"))
            return

        if response[0] == MSG_ROLE:
            self.role = response[1]
            # Actualizamos la GUI desde el hilo principal
            self.root.after(0, self.after_role)
        elif response[0] == MSG_ROOM_FULL:
            self.root.after(0, lambda: messagebox.showinfo(
                "Sala llena", "La sala esta llena, intenta mas tarde"))
            self.net.disconnect()

    def after_role(self):
        """Se llama después de recibir el rol — muestra pantalla de espera
           y arranca el hilo correspondiente segun el rol"""
        # Ambos roles empiezan esperando al segundo jugador
        self.show_waiting("Esperando al segundo jugador...")
        if self.role == ROLE_SETTER:
            threading.Thread(target=self.wait_for_second_player, daemon=True).start()
        else:
            threading.Thread(target=self.wait_for_board, daemon=True).start()

    """
    PANTALLA 2 — ESPERANDO
    """

    def show_waiting(self, message):
        """Pantalla de espera con spinner de puntos"""
        self.clear_frame()
        frame = self.make_frame()

        tk.Label(frame, text="HANGMAN", font=("Helvetica", 36, "bold"),
                 bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=(80, 5))

        # Guardamos el label del mensaje como atributo para poder actualizarlo
        self.waiting_message = tk.Label(frame, text=message, font=("Helvetica", 14),
                                        bg=BG_COLOR, fg=TEXT_COLOR)
        self.waiting_message.pack(pady=(40, 10))

        self.waiting_dots = tk.Label(frame, text="...", font=("Helvetica", 24),
                                      bg=BG_COLOR, fg=ACCENT_COLOR)
        self.waiting_dots.pack()

        # Animación de puntos
        self.animate_dots()
        self.add_nav_buttons(frame)

    def animate_dots(self):
        """Anima los puntos de espera"""
        try:
            if not self.current_frame:
                return
            current = self.waiting_dots.cget("text")
            next_dots = "." if len(current) >= 3 else current + "."
            self.waiting_dots.config(text=next_dots)
            self.root.after(500, self.animate_dots)
        except tk.TclError:
            # El frame ya fue destruido, detenemos la animación
            return

    def wait_for_second_player(self):
        """El setter espera al segundo jugador o recibe INGRESA_PALABRA directo"""
        response = self.net.receive()
        if not response:
            return

        if response[0] == "INGRESA_PALABRA":
            # El guesser ya estaba esperando, vamos directo a poner palabra
            self.root.after(0, self.show_setter)
        elif response[0] == MSG_WAIT:
            # Esperamos al guesser
            response = self.net.receive()
            if response and response[0] == "INGRESA_PALABRA":
                self.root.after(0, self.show_setter)

    def wait_for_board(self):
        """El guesser espera el tablero inicial.
           Flujo: WAIT (espera al setter) → WAITING_WORD (setter conectó) → BOARD (palabra lista)"""
        # Primer mensaje: WAIT — seguimos esperando al setter, no cambiamos el mensaje
        response = self.net.receive()

        if response and response[0] == MSG_WAIT:
            # El setter aun no conecta, seguimos esperando
            response = self.net.receive()

        # Segundo mensaje: WAITING_WORD — el setter ya conectó, ahora espera la palabra
        if response and response[0] == MSG_WAITING_WORD:
            self.root.after(0, lambda: self.waiting_message.config(
                text="Esperando a que el Setter elija una palabra..."))
            response = self.net.receive()

        # Tercer mensaje: BOARD — la palabra fue puesta, arranca el juego
        if response and response[0] == MSG_BOARD:
            self.board = response[1]
            self.root.after(0, self.show_guesser)

    """
    PANTALLA 3A — SETTER
    """

    def show_setter(self):
        """Pantalla del setter para ingresar la palabra"""
        self.clear_frame()
        frame = self.make_frame()

        tk.Label(frame, text="Tu rol: SETTER", font=("Helvetica", 28, "bold"),
                 bg=BG_COLOR, fg=GREEN_COLOR).pack(pady=(60, 5))
        tk.Label(frame, text="Elige la palabra que el otro jugador va a adivinar",
                 font=("Helvetica", 12), bg=BG_COLOR, fg=SUBTLE_COLOR).pack(pady=(0, 40))

        card = tk.Frame(frame, bg=CARD_COLOR, padx=40, pady=30)
        card.pack(padx=60)

        tk.Label(card, text="Escribe la palabra:", font=("Helvetica", 14),
                 bg=CARD_COLOR, fg=TEXT_COLOR).pack(anchor="w")

        self.word_entry = tk.Entry(card, font=("Helvetica", 18),
                                    bg="#0f3460", fg=GREEN_COLOR,
                                    insertbackground=GREEN_COLOR,
                                    relief="flat", width=20)
        self.word_entry.pack(pady=(5, 5), ipady=10)

        tk.Label(card, text="Solo letras A-Z. Puede ser en ingles o español sin acentos ni ñ",
                 font=("Helvetica", 10), bg=CARD_COLOR, fg=SUBTLE_COLOR).pack()
        tk.Label(card, text="Ejemplos: GATO, PERRO, COMPUTER, WINDOW",
                 font=("Helvetica", 10), bg=CARD_COLOR, fg=SUBTLE_COLOR).pack(pady=(0, 15))

        self.word_error = tk.Label(card, text="", font=("Helvetica", 11),
                                    bg=CARD_COLOR, fg=RED_COLOR)
        self.word_error.pack(pady=(0, 10))

        make_button(card, "Enviar palabra", self.do_send_word,
                    bg=GREEN_COLOR, fg=DARK_COLOR,
                    font_size=13, bold=True, padx=30, pady=10, width=20).pack()

        self.word_entry.bind("<Return>", lambda e: self.do_send_word())
        self.word_entry.focus()
        self.add_nav_buttons(frame)

    def do_send_word(self):
        """Manda la palabra al servidor y espera el resultado"""
        word = self.word_entry.get().strip()

        if not word:
            self.word_error.config(text="Por favor escribe una palabra")
            return

        if not all(c.isalpha() and c.isascii() for c in word):
            self.word_error.config(
                text="Solo letras A-Z, sin acentos ni caracteres especiales")
            return

        if len(word) < 2 or len(word) > 63:
            self.word_error.config(text="La palabra debe tener entre 2 y 63 letras")
            return

        # Mandamos la palabra al servidor
        self.net.send_word(word)

        # Esperamos respuesta del servidor en hilo separado
        threading.Thread(target=self.wait_for_setter_result, daemon=True).start()
        self.show_waiting("Palabra enviada. Esperando al Guesser...")

    def wait_for_setter_result(self):
        """El setter espera el resultado final de la partida"""
        # Primero recibimos el WAIT de confirmación
        response = self.net.receive()

        # Puede ser ERROR si la palabra no es válida
        if response and response[0] == MSG_ERROR:
            self.root.after(0, lambda: self.show_setter())
            self.root.after(0, lambda: self.word_error.config(text=response[1]))
            return

        # Esperamos WIN o LOSE
        response = self.net.receive()
        if response:
            if response[0] == MSG_WIN:
                self.root.after(0, lambda: self.show_result(True, response[1]))
            elif response[0] == MSG_LOSE:
                self.root.after(0, lambda: self.show_result(False, response[1]))

    """
    PANTALLA 3B — GUESSER
    """ 

    def show_guesser(self):
        """Pantalla del guesser con el ahorcado y el tablero"""
        self.clear_frame()
        frame = self.make_frame()

        tk.Label(frame, text="Tu rol: GUESSER", font=("Helvetica", 20, "bold"),
                 bg=BG_COLOR, fg=ACCENT_COLOR).pack(pady=(50, 5))

        # Dibujo del ahorcado
        self.hangman_canvas = tk.Canvas(
            frame, width=200, height=250, 
            bg=BG_COLOR, highlightthickness=0
        )
        self.hangman_canvas.pack(pady=(5,10))
        self.draw_hangman(self.wrong_attempts)

        # Tablero — letras adivinadas y guiones
        self.board_label = tk.Label(
            frame,
            text=self.format_board(self.board),
            font=("Helvetica", 28, "bold"),
            bg=BG_COLOR, fg=GREEN_COLOR
        )
        self.board_label.pack(pady=(5, 5))

        # Contador de intentos
        self.attempts_label = tk.Label(
            frame,
            text=f"Intentos fallidos: {self.wrong_attempts}/{MAX_ATTEMPTS}",
            font=("Helvetica", 12),
            bg=BG_COLOR, fg=SUBTLE_COLOR
        )
        self.attempts_label.pack(pady=(0, 15))

        # Input de letra
        card = tk.Frame(frame, bg=CARD_COLOR, padx=30, pady=20)
        card.pack(padx=60, fill="x")

        tk.Label(card, text="Adivina una letra:", font=("Helvetica", 13),
                 bg=CARD_COLOR, fg=TEXT_COLOR).pack(anchor="w")

        input_row = tk.Frame(card, bg=CARD_COLOR)
        input_row.pack(fill="x", pady=(5, 5))

        self.guess_entry = tk.Entry(input_row, font=("Helvetica", 18),
                                     bg="#0f3460", fg=TEXT_COLOR,
                                     insertbackground=TEXT_COLOR,
                                     relief="flat", width=5)
        self.guess_entry.pack(side="left", ipady=8, padx=(0, 10))

        make_button(input_row, "Adivinar", self.do_send_guess,
                    bg=ACCENT_COLOR, fg="white",
                    font_size=12, bold=True, padx=15, pady=8).pack(side="left")

        self.guess_error = tk.Label(card, text="", font=("Helvetica", 11),
                                     bg=CARD_COLOR, fg=RED_COLOR)
        self.guess_error.pack()

        self.guess_entry.bind("<Return>", lambda e: self.do_send_guess())
        self.guess_entry.focus()
        self.add_nav_buttons(frame)

    def format_board(self, board):
        """Formatea el tablero para mostrarlo con espacios entre letras"""
        return "  ".join(board)

    def do_send_guess(self):
        """Manda una letra al servidor"""
        letter = self.guess_entry.get().strip()
        self.guess_entry.delete(0, tk.END)

        if not letter:
            self.guess_error.config(text="Por favor escribe una letra")
            return

        if len(letter) != 1:
            self.guess_error.config(text="Solo puedes mandar una letra a la vez")
            return

        if not (letter.isalpha() and letter.isascii()):
            self.guess_error.config(text="Solo se permiten letras A-Z")
            return

        self.net.send_guess(letter)
        threading.Thread(target=self.wait_for_guess_result, daemon=True).start()

    def wait_for_guess_result(self):
        """Espera la respuesta del servidor al intento"""
        response = self.net.receive()
        if not response:
            return

        cmd = response[0]

        if cmd == MSG_ERROR:
            # Letra ya intentada u otro error
            self.root.after(0, lambda: self.guess_error.config(text=response[1]))

        elif cmd == MSG_CORRECT:
            # Letra correcta — actualizamos tablero
            self.board = response[1]
            self.wrong_attempts = int(response[2])
            self.root.after(0, self.update_guesser_ui)
            self.root.after(0, lambda: self.guess_error.config(
                text="¡Letra correcta!", **{"fg": GREEN_COLOR}))

        elif cmd == MSG_WRONG:
            # Letra incorrecta — actualizamos intentos
            self.board = response[1]
            self.wrong_attempts = int(response[2])
            self.root.after(0, self.update_guesser_ui)
            self.root.after(0, lambda: self.guess_error.config(
                text="Letra incorrecta", **{"fg": RED_COLOR}))

        elif cmd == MSG_WIN:
            self.board = list(response[1])
            self.root.after(0, lambda: self.guess_error.config(
                text="Salvado!", fg=GREEN_COLOR))
            self.root.after(0, self.update_guesser_ui)
            self.root.after(5000, lambda: self.show_result(True, response[1]))

        elif cmd == MSG_LOSE:
            self.wrong_attempts = 6
            self.root.after(0, self.update_guesser_ui)
            self.root.after(0, lambda: self.guess_error.config(
                text="¡Ahorcado!", fg=RED_COLOR))
            self.root.after(5000, lambda: self.show_result(False, response[1]))

    def update_guesser_ui(self):
        """Actualiza el ahorcado, tablero e intentos en pantalla"""
        if self.wrong_attempts >= 6:
            stage = 6  
        elif self.board and '_' not in self.board:
            stage = 7  
        else:
            stage = self.wrong_attempts
        self.draw_hangman(stage)
        self.board_label.config(text=self.format_board(self.board))
        self.attempts_label.config(
            text=f"Intentos fallidos: {self.wrong_attempts}/{MAX_ATTEMPTS}")
        
    def draw_hangman(self, stage):
        """Dibuja el ahorcado con gradiente de color, torso relleno y cara de victoria"""
        self.hangman_canvas.delete("all")  # Limpiar dibujo anterior
        
        gallows_color = SUBTLE_COLOR   # Gris para la horca
        all_body_color = "white"     # Partes blancas
        win_color = GREEN_COLOR      # Verde victoria
        
        def get_gradient_color(step):
            # RGB de #eaeaea (TEXT_COLOR / Blanco base)
            r1, g1, b1 = 234, 234, 234
            # RGB de #e94560 (ACCENT_COLOR / Rojo)
            r2, g2, b2 = 233, 69, 96
            
            if step >= 6: step = 5

            r = int(r1 + (r2 - r1) * (step / 5.0))
            g = int(g1 + (g2 - g1) * (step / 5.0))
            b = int(b1 + (b2 - b1) * (step / 5.0))
            
            return f'#{r:02x}{g:02x}{b:02x}'

    
        # Plataforma
        self.hangman_canvas.create_line(30, 230, 170, 230, fill=gallows_color, width=8, capstyle=tk.ROUND)
        # Poste principal
        self.hangman_canvas.create_line(50, 230, 50, 20, fill=gallows_color, width=8, capstyle=tk.ROUND)
        # Viga superior
        self.hangman_canvas.create_line(46, 20, 120, 20, fill=gallows_color, width=8, capstyle=tk.ROUND)
        # Soporte diagonal (hace que la horca se vea mejor construida)
        self.hangman_canvas.create_line(50, 60, 90, 20, fill=gallows_color, width=6, capstyle=tk.ROUND)
        # Cuerda
        self.hangman_canvas.create_line(120, 20, 120, 45, fill="white", width=3)


        if stage >= 1 and stage != 7:
            # Definir color de contorno
            if stage >= 6: head_outline = ACCENT_COLOR # Derrota = Rojo
            else: head_outline = get_gradient_color(stage) # Proceso = Gradiente
            
            # Contorno de la cabeza
            self.hangman_canvas.create_oval(100, 45, 140, 85, fill=BG_COLOR, outline=head_outline, width=4)
            
            # Dibujar Cara Viva (Nervios)
            if stage < 6:
                eye_color = head_outline # Los ojos cambian con el gradiente
                # Ojos
                self.hangman_canvas.create_oval(110, 58, 114, 62, fill=eye_color, outline="")
                self.hangman_canvas.create_oval(126, 58, 130, 62, fill=eye_color, outline="")
                # Boca de nervios
                self.hangman_canvas.create_line(116, 72, 124, 72, fill=eye_color, width=2, capstyle=tk.ROUND)

        # 5. Dibujar Cuerpo (REQUISITO 1: Relleno)
        # Usamos un rectángulo para el torso, con fill (relleno) y outline (borde blanco)
        if stage >= 2 or stage == 7: # Ambos necesitan el torso relleno
            if stage == 7: current_body = win_color
            else: current_body = all_body_color
            
            # Torso Relleno: x1, y1, x2, y2 (x1-x2 define grosor, y1-y2 define altura)
            self.hangman_canvas.create_rectangle(114, 85, 126, 145, fill=current_body, outline=current_body, width=0)

        # 6. Extremidades (REQUISITO 2: Blancas)
        # Brazo Izquierdo
        if stage >= 3 or stage == 7: 
            limb_color = win_color if stage == 7 else all_body_color
            self.hangman_canvas.create_line(114, 95, 95, 115, 105, 135, fill=limb_color, width=5, capstyle=tk.ROUND, joinstyle=tk.ROUND)

        # Brazo Derecho
        if stage >= 4 or stage == 7: 
            limb_color = win_color if stage == 7 else all_body_color
            self.hangman_canvas.create_line(126, 95, 145, 115, 135, 135, fill=limb_color, width=5, capstyle=tk.ROUND, joinstyle=tk.ROUND)

        # Pierna Izquierda
        if stage >= 5 or stage == 7: 
            limb_color = win_color if stage == 7 else all_body_color
            self.hangman_canvas.create_line(114, 140, 100, 170, 105, 200, fill=limb_color, width=6, capstyle=tk.ROUND, joinstyle=tk.ROUND)

        # Pierna Derecha, Derrota y Victoria (Requisito 3)
        if stage >= 6 or stage == 7: 
            # Victoria (REQUISITO 3)
            if stage == 7:
                limb_color = win_color
                # Pierna Derecha Victoria
                self.hangman_canvas.create_line(126, 140, 140, 170, 135, 200, fill=win_color, width=6, capstyle=tk.ROUND, joinstyle=tk.ROUND)
                
                # REQUISITO 3: Cabeza Verde, Expresión Feliz (^_^)
                self.hangman_canvas.create_oval(100, 45, 140, 85, fill=BG_COLOR, outline=win_color, width=4)
                
                # Ojos (Arco hacia arriba)
                # Ojo Izquierdo
                self.hangman_canvas.create_arc(106, 52, 118, 68, start=0, extent=180, style=tk.ARC, outline=win_color, width=3)
                # Ojo Derecho
                self.hangman_canvas.create_arc(122, 52, 134, 68, start=0, extent=180, style=tk.ARC, outline=win_color, width=3)
                
                # REQUISITO 3: Sonrisa (U) (Arco hacia abajo)
                self.hangman_canvas.create_arc(110, 68, 130, 82, start=180, extent=180, style=tk.ARC, outline=win_color, width=3)

            # Derrota (Stage 6) (Sigue igual, pero con las extremidades blancas)
            else:
                # Pierna Derecha Derrota (Blanca)
                self.hangman_canvas.create_line(126, 140, 140, 170, 135, 200, fill=all_body_color, width=6, capstyle=tk.ROUND, joinstyle=tk.ROUND)
                
                # Expresión de muerto (X_X / Rojo)
                # Limpiamos el interior
                self.hangman_canvas.create_oval(102, 47, 138, 83, fill=BG_COLOR, outline="")
                # Ojos de muerto (X_X)
                self.hangman_canvas.create_line(108, 56, 116, 64, fill=ACCENT_COLOR, width=3, capstyle=tk.ROUND)
                self.hangman_canvas.create_line(116, 56, 108, 64, fill=ACCENT_COLOR, width=3, capstyle=tk.ROUND)
                self.hangman_canvas.create_line(124, 56, 132, 64, fill=ACCENT_COLOR, width=3, capstyle=tk.ROUND)
                self.hangman_canvas.create_line(132, 56, 124, 64, fill=ACCENT_COLOR, width=3, capstyle=tk.ROUND)
                # Boca triste (arco hacia abajo)
                self.hangman_canvas.create_arc(110, 75, 130, 85, start=0, extent=180, style=tk.ARC, outline=ACCENT_COLOR, width=3)

    """
    PANTALLA 4 — RESULTADO
    """

    def show_result(self, won, word):
        """Pantalla de resultado — WIN o LOSE"""
        self.clear_frame()
        frame = self.make_frame()

        if won:
            tk.Label(frame, text="¡GANASTE!", font=("Helvetica", 48, "bold"),
                    bg=BG_COLOR, fg=GREEN_COLOR).pack(pady=(80, 10))
            if self.role == ROLE_SETTER:
                msg = "El guesser no adivino tu palabra"
            else:
                msg = "Adivinaste la palabra"
            tk.Label(frame, text=msg, font=("Helvetica", 16),
                    bg=BG_COLOR, fg=SUBTLE_COLOR).pack()
        else:
            tk.Label(frame, text="PERDISTE", font=("Helvetica", 48, "bold"),
                    bg=BG_COLOR, fg=RED_COLOR).pack(pady=(80, 10))
            if self.role == ROLE_SETTER:
                msg = "El guesser adivino tu palabra"
            else:
                msg = "Se acabaron los intentos"
            tk.Label(frame, text=msg, font=("Helvetica", 16),
                    bg=BG_COLOR, fg=SUBTLE_COLOR).pack()

        tk.Label(frame, text=word, font=("Helvetica", 36, "bold"),
                 bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=(20, 40))

        make_button(frame, "Jugar de nuevo", self.restart,
                    bg=ACCENT_COLOR, fg="white",
                    font_size=14, bold=True, padx=20, pady=10).pack()

        self.add_nav_buttons(frame)

    def restart(self):
        """Reinicia el cliente para jugar otra ronda"""
        self.net.disconnect()
        self.role = None
        self.wrong_attempts = 0
        self.board = ""
        #Se crea un NetworkClient nuevo para siguiente rondas
        self.net = NetworkClient(self.net.host, self.net.port)
        self.show_login()

    """ 
    VENTANA ACERCA DE
    """ 

    def show_about(self):
        """Abre la ventana de Acerca de — muestra créditos del proyecto"""
        about = tk.Toplevel(self.root)
        about.title("Acerca de")
        about.geometry("420x560")
        about.configure(bg="white")
        about.resizable(False, False)

        # Título UP
        tk.Label(about, text="UP", font=("Helvetica", 36, "bold"),
                 bg="white", fg="#1a1a2e").pack(pady=(30, 10))

        # Título del proyecto
        tk.Label(about, text="Proyecto 2do Parcial: Hangman",
                 font=("Georgia", 16, "bold"),
                 bg="white", fg="#1a1a2e").pack(pady=(10, 20))

        # Carrera
        tk.Label(about,
                 text="Ingeniería en Sistemas y Gráficas Computacionales",
                 font=("Georgia", 12),
                 bg="white", fg="#333333").pack()

        # Integrantes
        tk.Label(about, text="\nCarlos J. Zepeda",
                 font=("Georgia", 12), bg="white", fg="#333333").pack()
        tk.Label(about, text="José M. Paredes",
                 font=("Georgia", 12), bg="white", fg="#333333").pack()
        tk.Label(about, text="Omar S. Lopez",
                 font=("Georgia", 12), bg="white", fg="#333333").pack()

        # Escuela y universidad
        tk.Label(about, text="\nEscuela de Ingeniería",
                 font=("Georgia", 12), bg="white", fg="#333333").pack()
        tk.Label(about, text="Universidad Panamericana Guadalajara",
                 font=("Georgia", 12), bg="white", fg="#333333").pack()

        # Materia y profesor
        tk.Label(about, text="\nCDS: Cómputo Distribuido",
                 font=("Georgia", 12), bg="white", fg="#333333").pack()
        tk.Label(about, text="Dr. Juan L. Pimentel",
                 font=("Georgia", 12), bg="white", fg="#333333").pack(pady=(0, 20))

        # Botón cerrar
        make_button(about, "Cerrar", about.destroy,
                    bg=DARK_COLOR, fg="white",
                    font_size=11, padx=20, pady=6).pack()

    """ 
    VENTANA CÓMO JUGAR
    """ 

    def show_how_to_play(self):
        """Abre la ventana de instrucciones detalladas del juego"""
        how = tk.Toplevel(self.root)
        how.title("Cómo jugar")
        how.geometry("480x680")
        how.configure(bg="white")
        how.resizable(False, False)

        # Scrollable frame para que quepan todas las instrucciones
        canvas = tk.Canvas(how, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(how, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="white")

        scroll_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Título
        tk.Label(scroll_frame, text="Cómo jugar Hangman",
                 font=("Georgia", 18, "bold"),
                 bg="white", fg="#1a1a2e").pack(pady=(20, 5))
        tk.Label(scroll_frame, text="Guía completa del juego",
                 font=("Georgia", 12), bg="white", fg="#888").pack(pady=(0, 20))

        tk.Frame(scroll_frame, bg="#dddddd", height=1).pack(fill="x", padx=20)

        # OBJETIVO
        tk.Label(scroll_frame, text="\nOBJETIVO",
                 font=("Georgia", 13, "bold"), bg="white", fg="#1a1a2e").pack(anchor="w", padx=20)
        tk.Label(scroll_frame,
                 text="Pon una palabra que tu oponente no pueda adivinar\no adivina la palabra secreta de tu oponente\nantes de que el ahorcado se complete.",
                 font=("Georgia", 11), bg="white", fg="#333333", justify="left").pack(anchor="w", padx=30, pady=(5, 10))

        tk.Frame(scroll_frame, bg="#dddddd", height=1).pack(fill="x", padx=20)

        # ROLES
        tk.Label(scroll_frame, text="\nROLES",
                 font=("Georgia", 13, "bold"), bg="white", fg="#1a1a2e").pack(anchor="w", padx=20)

        tk.Label(scroll_frame, text="SETTER:",
                 font=("Georgia", 12, "bold"), bg="white", fg="#4ecca3").pack(anchor="w", padx=30, pady=(5, 0))
        tk.Label(scroll_frame,
                 text="• Elige la palabra secreta que el otro jugador\n  debe adivinar. ¡Ponla difícil!\n• Solo letras A-Z, sin acentos ni ñ.\n• Puede ser en inglés o español.\n• Ejemplos: GATO, COMPUTER, PERRO, WINDOW",
                 font=("Georgia", 11), bg="white", fg="#333333", justify="left").pack(anchor="w", padx=40, pady=(2, 10))

        tk.Label(scroll_frame, text="GUESSER:",
                 font=("Georgia", 12, "bold"), bg="white", fg="#e94560").pack(anchor="w", padx=30, pady=(5, 0))
        tk.Label(scroll_frame,
                 text="• Adivina la palabra letra por letra.\n• Cada letra incorrecta agrega una parte\n  al ahorcado.\n• Tienes 6 intentos fallidos antes de perder.\n• No puedes repetir letras ya intentadas.",
                 font=("Georgia", 11), bg="white", fg="#333333", justify="left").pack(anchor="w", padx=40, pady=(2, 10))

        tk.Frame(scroll_frame, bg="#dddddd", height=1).pack(fill="x", padx=20)

        # CÓMO SE JUEGA
        tk.Label(scroll_frame, text="\nCÓMO SE JUEGA",
                 font=("Georgia", 13, "bold"), bg="white", fg="#1a1a2e").pack(anchor="w", padx=20)
        pasos = [
            "1. Ambos jugadores inician sesión con su usuario\n   y contraseña.",
            "2. Ronda 1: el primero en conectar es SETTER,\n   el segundo es GUESSER.\n   Ronda 2: los roles se invierten, el primero\n   ahora es GUESSER y el segundo es SETTER.",
            "3. El SETTER escribe la palabra secreta y espera.",
            "4. El GUESSER ve el tablero con guiones ( _ )\n   representando cada letra de la palabra.",
            "5. El GUESSER ingresa una letra a la vez.\n   Si está en la palabra, se revela su posición.\n   Si no está, se dibuja una parte del ahorcado.",
            "6. La ronda termina cuando el GUESSER adivina\n   la palabra completa o se queda sin intentos.",
            "7. Al terminar la ronda la sesión se cierra\n   automáticamente. Ambos jugadores vuelven\n   a la pantalla de login para jugar otra ronda\n   con los roles intercambiados.",
        ]
        for paso in pasos:
            tk.Label(scroll_frame, text=paso,
                     font=("Georgia", 11), bg="white", fg="#333333", justify="left").pack(anchor="w", padx=30, pady=3)

        tk.Frame(scroll_frame, bg="#dddddd", height=1).pack(fill="x", padx=20, pady=(10, 0))

        # CÓMO SE GANA
        tk.Label(scroll_frame, text="\nCÓMO SE GANA",
                 font=("Georgia", 13, "bold"), bg="white", fg="#1a1a2e").pack(anchor="w", padx=20)
        tk.Label(scroll_frame,
                 text="GUESSER gana: adivina todas las letras antes\nde cometer 6 errores.",
                 font=("Georgia", 11), bg="white", fg="#333333", justify="left").pack(anchor="w", padx=30, pady=(5, 3))
        tk.Label(scroll_frame,
                 text="SETTER gana: el guesser comete 6 errores\nsin adivinar la palabra completa.",
                 font=("Georgia", 11), bg="white", fg="#333333", justify="left").pack(anchor="w", padx=30, pady=(3, 10))

        tk.Frame(scroll_frame, bg="#dddddd", height=1).pack(fill="x", padx=20)

        # USUARIOS DE PRUEBA
        tk.Label(scroll_frame, text="\nUSUARIOS DE PRUEBA",
                 font=("Georgia", 13, "bold"), bg="white", fg="#1a1a2e").pack(anchor="w", padx=20)
        usuarios = [
            ("carlos",  "1234"),
            ("omar",    "4321"),
            ("padrino", "0000"),
            ("marco",   "5678"),
            ("ana",     "abcd"),
            ("luis",    "pass1"),
            ("sofia",   "qwerty"),
        ]
        for user, pwd in usuarios:
            tk.Label(scroll_frame,
                     text=f"Usuario: {user:<10}  Contraseña: {pwd}",
                     font=("Courier", 11), bg="white", fg="#333333").pack(anchor="w", padx=30, pady=1)

        # Botón cerrar
        make_button(scroll_frame, "Cerrar", how.destroy,
                    bg=DARK_COLOR, fg="white",
                    font_size=11, padx=20, pady=6).pack(pady=20)

    """
    INICIO
    """

    def run(self):
        """Arranca el loop principal de tkinter"""
        self.root.mainloop()