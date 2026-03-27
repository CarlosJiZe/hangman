#ifndef AUTH_H
#define AUTH_H

/* FUNCIONES PARA LA AUTENTICACIÓN DE USUARIOS */

//Numero maximo de usuarios registrados
#define MAX_USERS 100

//Tamaño maximo de usuario y contraseña
#define MAX_USERNAME 32
#define MAX_PASSWORD 32

//Estructura para almacenar la información de un usuario
typedef struct{
    char username[MAX_USERNAME];
    char password[MAX_PASSWORD];
} User;

//load_users carga los usuarios registrados desde el archivo "users.txt"
// Retorna el numero de usuarios cargados, o -1 si hay error
int load_users(const char* filename);

//authenticate verifica si el username y password son correctos
// Retorna 1 si son correctos, 0 si no
int authenticate(const char* username, const char* password);

#endif //AUTH_H