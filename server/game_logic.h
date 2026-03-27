#ifndef GAME_LOGIC_H
#define GAME_LOGIC_H

#include "../shared/protocol.h"

/* FUNCIONES Y ESTRUCTURAS PARA EL JUEGO DEL AHORCADO */

//Estados posible de la partida
typedef enum{
    STATE_WAITING, //Esperando a que esten los 2 jugadores
    STATE_SETTING_WORD, //El setter esta eligiendo la palabra
    STATE_PLAYING, //El guesser esta adivinando la palabra
    STATE_GAME_OVER //La partida termino
}GameStatus;

//GameState es una estructura que en memoria comparida (mmap)
// Esto tiene el objetivo de que ambos hijos pueda leerlo y escribir en él

typedef struct{
    char word[MAX_WORD]; //La palabra a adivinar, solo el setter la conoce
    char board[MAX_WORD]; //Tablero que se muestra al guesser, con las letras adivinadas y _ para las que faltan
    char guessed[26]; //Letras ya intentadas A-Z
    int wrong_attempts; //Numero de intentos fallidos acumulados
    int setter_fd; //File descriptor del setter, es basicamente el socker
    int guesser_fd; //File descriptor del guesser, tambien es el socket
    int players_connected; //Cuantos jugadores hay conectados
    int game_over; //0 si la partida sigue, 1 si la partida termino
    int round; //Numero de ronda

    GameStatus status; //Estado actual de la partida
}GameState;

/* FUNCIONES */

//init_game_state inicia el GameState en memoria compartida
//Se inicializa en 0 o vacio para iniciar la partida limpia

void init_game_state(GameState *gs);

//set_word, sirve para que cuando el setter mande la palabra se guarda y se contruye el tablero

void set_word(GameState *gs, const char *word);

//process_guess, cuando el guesser manda una letra, se busca la letra en la palabra y se actualiza el tablero
// 1 si esta la letra, 0 si no esta la letra, -1 si la letra ya se habia intentado

int process_guess(GameState *gs, char letter);

//check_win, revisa si el guesser ya adivino toda la palabra
// 1 si gano, 0 si no ha ganado aun

int check_win(GameState *gs);

//check_lose, revisa si el guesser ya se quedo sin intentos
// 1 si perdio, 0 si no ha perdido aun

int check_lose(GameState *gs);

#endif //GAME_LOGIC_H