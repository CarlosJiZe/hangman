#ifndef PROTOCOL_H
#define PROTOCOL_H

/*
    Definición del protocolo de comunicación entre el cliente y el servidor
    Todos los mensajes son strings que terminan con '\n'
    El formato de los mensajes es el siguiente:
      - General: COMANDO:arg1:arg2\n
*/ 

// Tamaño maximo de cualquier mensaje en la red
#define MAX_MSG 256

// Tamaño maximo de una palabra en el juego
#define MAX_WORD 64

// Puerto donde escucha el servidor
#define PORT 5000

/*
    MENSAJES DEL CLIENTE AL SERVIDOR
*/

// Login para que el cliente mande usuario y contraseña
// Ejemplo "LOGIN:carlos:1234\n"
#define MSG_LOGIN "LOGIN"

// El jugador 1 manda la palabra a adivinar
// Ejemplo "SET_WORD:computadora\n"
#define MSG_SET_WORD "SET_WORD"

// El jugador 2 manda una letra para adivinar
// Ejemplo "GUESS:A\n"
#define MSG_GUESS "GUESS"

/*
    MENSAJES DEL SERVIDOR AL CLIENTE
*/

//Inicio de sesion adecuado
// Ejmplo "LOGIN_OK\n"
#define MSG_LOGIN_OK "LOGIN_OK"

//Inicio de sesion fallido
// Ejemplo "LOGIN_FAIL\n"
#define MSG_LOGIN_FAIL "LOGIN_FAIL"

// El servidor notifica al cliente cual es su rol en la partida
// Ejemplo "ROLE:SETTER\n" es el jugador que pone la palabra
// Ejemplo "ROLE:GUESSER\n" es el jugador que adivina
#define MSG_ROLE "ROLE"
#define ROLE_SETTER "SETTER"
#define ROLE_GUESSER "GUESSER"

// El servidor manda el estado actual de juego
// El servidor manda las letras adivinadas y _ para las que faltan
// Ejemplo "BOARD:C_MP_TAD_R_\n"
#define MSG_BOARD "BOARD"

// El servidor notifica al cliente si la letra esta en la palabra
// Ejemplo "CORRECT:C_MP_TAD_R_\n" 
#define MSG_CORRECT "CORRECT"

// El servidor notifica al cliente si la letra no esta en la palabra
// Ejemplo "WRONG:C_MP_TAD_R_\n"
#define MSG_WRONG "WRONG"

// El servidor informa al cliente si ya se adivino toda la palabra
// Ejemplo "WIN:COMPUTADORA\n"
#define MSG_WIN "WIN"

// El servidor informa al cliente si se acabaron los intentos
// Ejemplo "LOSE:COMPUTADORA\n" Se revela la palabra correcta
#define MSG_LOSE "LOSE"

//El servidor avisa que hay que esperar al otro jugador
//Ejmplo "WAIT\n"
#define MSG_WAIT "WAIT"

//El servidor informa si el otro jugador se desconecto
//Ejemplo "OPPONENT_LEFT\n"
#define MSG_OPPONENT_LEFT "OPPONENT_LEFT"

//El servidor informa a un tercer cliente que la sala esta llena (ya hay dos jugadores)
//Ejemplo "ROOM_FULL\n"
#define MSG_ROOM_FULL "ROOM_FULL"

//El servidor avisa que hubo un errror en la validacion de la palabra
//Ejemplo "ERROR: Solo se permiten letras A-Z\n"
//Ejemplo "ERROR: La palabra ya fue establecida\n"
#define MSG_ERROR "ERROR"

//El servidor avisa al guesser que debe esperar a que el setter ponga la palabra
//Se manda cuando ya conectaron los 2 jugadores pero el setter aun no ha puesto la palabra
//Ejemplo "WAITING_WORD\n"
#define MSG_WAITING_WORD "WAITING_WORD"

/*
    CONSTANTES DEL JUEGO
*/

// Numero maximo de intentos para adivinar la palabra
#define MAX_ATTEMPTS 6

// Numero maximo de jugadores en una sala
#define MAX_PLAYERS 2

#endif // PROTOCOL_H
