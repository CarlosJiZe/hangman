#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include "game_logic.h"

/* IMPLEMENTACION DE LAS FUNCIONES DEL JUEGO DEL AHORCADO */

//init_game_state, limpia el GameState para iniciar una partida nueva
//Se llama al inicio y entre rondas cuando cambian roles

void init_game_state(GameState *gs){
    memset(gs->word,0,sizeof(gs->word)); //Limpiamos la palabra
    memset(gs->board,0,sizeof(gs->board)); //Limpiamos el tablero
    memset(gs->guessed,0,sizeof(gs->guessed)); //Limpiamos la letras intentadas
    gs->wrong_attempts = 0; //Dejamos en 0 los intentos fallidos
    gs->game_over =0; //La partida no ha terminado
    gs->status = STATE_WAITING; //Esperamos a que se conecten los jugadores
    //Los demas no se limpian porque de eso se encarga el servidor
}

//set_word, guarda la palabra que manda el setter

void set_word(GameState *gs, const char *word){
    int i;
    int len = strlen(word);

    //Hacemos una copia de la palabra en mayusculas
    for(i=0; i<len && i< MAX_WORD-1;i++){
        gs->word[i]= toupper((unsigned char)word[i]);
    }
    gs->word[i] = '\0'; //Terminamos el string

    //Construimos el tablero con _ para cada letra
    for (i=0; i<len;i++){
        gs->board[i]= '_';
    }
    gs->board[i] = '\0'; //Terminamos el string

    printf("[juego] Palabra establecida: %s (tablero: %s)\n",gs->word,gs->board);
    fflush(stdout);
}

//process_guess, procesa un intento del guesser


int process_guess(GameState *gs, char letter){
    int i;
    int found = 0;
    int len = strlen(gs->word);

    // 1. Convertimos la letra a mayuscula
    
    letter = toupper((unsigned char)letter);

    // Revisamos si la letra ya se intento antes
    // 2. guessed es un array de 26 caracteres para las letras A-Z, si guessed[0] = 'A' significa que la letra A ya se intento

    int idx = letter - 'A'; //Convertimos las letras
    if(idx < 0 || idx > 25){
        return -1; //Letra no valida
    }

    if(gs->guessed[idx]){
        return -1; //Letra ya se intento
    }

    // 3. Marcamos la letra como intentada
    gs->guessed[idx] = 1;

    // 4. Ahora si buscamos la letra en la palabra y actualizamos el tablero
    for(i = 0; i<len; i++){
        if(gs->word[i] ==letter){
            gs->board[i] = letter; //Si la letra esta en la palabra, la mostramos en el tablero
            found = 1; //Marcamos que encontramos la letra
        }
    }
    // 5. Si no encontramos la letra, incrementamos los intentos fallidos
    if(!found){
        gs->wrong_attempts++; //Si no encontramos la letra, incrementamos los intentos fallidos
        printf("[juego] Letra '%c' incorrecta. Intentos fallidos: %d/%d\n",letter, gs->wrong_attempts, MAX_ATTEMPTS);
    }else{ // 6. Si encontramos la letra, mostramos el tablero actualizado
        printf("[juego] Letra '%c' correcta. Tablero: %s\n", letter, gs->board);
    }
    fflush(stdout);

    return found; //Regresamos si la letra estaba o no en la palabra
    //1 si esta la letra, 0 si no
}

//check_win, revisa si el tablero no tiene '_'

int check_win(GameState *gs){
    int i;
    for(i = 0; i<(int)strlen(gs->board);i++){
        if(gs->board[i]=='_'){
            return 0; //Si hay un _ significa que no han adivinado toda la palabra
        }
    }
    return 1; //Si no hay _ significa que han adivinado toda la palabra
}

//check_lose, revisa si los intentos fallidos llegaron al maximo

int check_lose(GameState *gs){
    return gs->wrong_attempts >= MAX_ATTEMPTS; //Si los intentos fallidos son mayores o iguales al maximo, el guesser perdio
}

