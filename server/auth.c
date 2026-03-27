/* IMPLEMENTACIÓN DE LAS FUNCIONES DE AUTENTICACIÓN */
// Los usuarios se almacenan en users.txt de la siguiente forma:
// username:password
// Ejemplo: carlos:1234

//Librerias
#include <stdio.h>
#include <string.h>
#include "auth.h"

//Array para almacenar los usuarios cargados
static User users[MAX_USERS]; //Es global para que load_users y authenticate puedan acceder a el

//Numero de usuarios cargados
static int num_users = 0; // Es statico para que solo sea visible en este archivo

//load_users
int load_users(const char *filename){
    FILE *file;
    char line[MAX_USERNAME + MAX_PASSWORD + 2]; //Espacio para username, password, : y \n

    file = fopen(filename,"r"); //Abrimos el archivo en modo lectura
    if(file == NULL){
        perror("Error al abrir el archivo de usuarios");
        return -1;
    }

    num_users = 0; //Reiniciamos el contador de usuarios

    //Leemos el archivo linea por linea o hasta que lleguemos al maximo de usuarios
    while(fgets(line,sizeof(line),file)!= NULL && num_users < MAX_USERS){
        if(sscanf(line, "%31[^:\n]:%31[^\n]", users[num_users].username, users[num_users].password)==2){ //Se divide la linea por medio de :
            num_users++; //Si la linea se parseo correctamente, incrementamos el contador de usuarios
        } else {
            fprintf(stderr, "Linea mal formateada en el archivo de usuarios: %s", line);
        }

    }
    fclose(file);
    printf("Usuarios cargados: %d\n", num_users);
    fflush(stdout);
    return num_users;
}

//authenticate
//Buscamos el username y la contraseña en el array de usuarios cargados
//Regresamos 1 si el username y password son correctos, 0 si no

int authenticate(const char *username, const char *password){
    int i;

    for(i = 0; i < num_users; i++){ //Iteramos por todos los usuarios cargados
        if(strcmp(users[i].username, username)== 0 && strcmp(users[i].password,password)==0){
            return 1; //Usuario y contraseña correctos
        }
    }
    return 0; //Usuario o contraseña incorrectos
}