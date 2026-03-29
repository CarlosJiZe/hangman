//Librerias necesaris
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <ctype.h>
#include <sys/wait.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/mman.h>
#include <semaphore.h>
#include "auth.h"
#include "game_logic.h"
#include "../shared/protocol.h"

/* ------------------------------------------
 ESTRUCTURA DEL SERVIDOR TCP CON FORK
------------------------------------------ */

/* ------------------------------------------
VARIABLES GLOBALES DE MEMORIA COMPARTIDA 
------------------------------------------ */
//Esta memoria se crea en el padre antes del fork para que se comparta la misma memoria

//Puntero al GameState en memoria compartida
static GameState *gs = NULL;

//Semaforo para sincronizar el acceso al GameState
static sem_t *game_sem = NULL;

/* ------------------------------------------
FUNCIONES AUXILIARES
------------------------------------------ */

//is_valid_letter, revisa si el caracter es una letra valida para adivinar (A-Z o a-z)
int is_valid_letter(char c){
    return (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z');
}

//is__valid_word, revisa si toda la palabra es valida, es decir, que solo contenga letras y no este vacia
// Minimo 2 letras y maximo MAX_WORD-1 letras
int is_valid_word(const char *word){
    int len = strlen(word);
    int i;
    if(len < 2 || len > MAX_WORD-1){
        return 0; //Palabra muy corta o muy larga
    }
    for(i=0; i<len; i++){
        if(!is_valid_letter(word[i])){
            return 0; //Caracter no valido en la palabra
        }
    }
    return 1; //Palabra valida
}

//signal_handler para evitar procesos zombies
//SIGCHLD es la señal que se manda cuando un hijo termina
//waitpid con WNOHANG se lleva a los hijos terminado pero no se queda bloqueado esperando a que terminen
void signal_handler(int sig){
    (void)sig; // Evitar advertencia de variable no usada
    while(waitpid(-1,NULL,WNOHANG)>0);
}

/* ------------------------------------------
HANDLER DE CLIENTE
------------------------------------------ */

//handle_client, esto es lo que ejecuta cada hijo
//Recibe el file descriptor del socket del cliente
void handle_client(int client_fd, struct sockaddr_in client_addr){
    char buffer[MAX_MSG];
    char username[MAX_USERNAME]; //Variables para almacenar el username y password que mande el cliente
    char password[MAX_PASSWORD];
    int bytes; //Variable para almacenar el numero de bytes recibidos del cliente
    int my_role; // 0 es setter, 1 es guesser

    //inet_ntoa convierte la direccion IP del cliente a formato legible
    printf("[hijo %d] Cliente conectado desde %s\n",getpid(),inet_ntoa(client_addr.sin_addr));
    fflush(stdout); //Aseguramos que el mensaje se imprima antes de cualquier otra cosa

    /* ------------------------------------------
    PROCESO DE AUTENTICACIÓN
    ------------------------------------------ */

    //Esperamos a que el cliente mande el mensaje de login
    bytes = recv(client_fd, buffer, sizeof(buffer)-1,0); //recv bloquea hasta que el cliente mande algo
    if(bytes <= 0){
        printf("[hijo %d] Cliente desconectado antes de hacer el login\n",getpid());
        fflush(stdout);
        close(client_fd); //Cerramos el socket del cliente
        return; //Terminamos la función
    }

    buffer[bytes] = '\0'; //Terminamos el string con null para poder usar funciones de string

    // Quitamos el \r si telnet lo manda (manda \r\n en lugar de \n) esto es por el unit testing que estamos haciendo
    // Esto evita que el password llegue como "1234\r" y no coincida
    for(int i = 0; i < bytes; i++){
        if(buffer[i] == '\r') buffer[i] = '\0';
    }

    //Parseamos el mensaje de login
    if(sscanf(buffer, "LOGIN:%31[^:]:%31[^\n]",username,password)!=2){
        //Mensaje mal formateado
        snprintf(buffer,sizeof(buffer),"%s\n",MSG_LOGIN_FAIL);
        send(client_fd, buffer, strlen(buffer),0); //Enviamos el mensaje de login fallido
        printf("[hijo %d] Formato de login invalido\n",getpid());
        fflush(stdout);
        close(client_fd); //Cerramos el socket del cliente
        return; //Terminamos la función
    }

    //Validamos el username y password con la función authenticate
    if(authenticate(username,password)){
        //Login exitoso
        snprintf(buffer,sizeof(buffer),"%s\n",MSG_LOGIN_OK);
        send(client_fd, buffer, strlen(buffer),0); //Enviamos el mensaje de login exitoso
        printf("[hijo %d] Login exitoso: %s\n",getpid(),username);
        fflush(stdout);
    } else {
        //Login fallido
        snprintf(buffer,sizeof(buffer),"%s\n",MSG_LOGIN_FAIL);
        send(client_fd, buffer, strlen(buffer),0); //Enviamos el mensaje de login fallido
        printf("[hijo %d] Login fallido: %s\n",getpid(),username);
        fflush(stdout);
        close(client_fd); //Cerramos el socket del cliente
        return; //Terminamos la función
    }

    /* ------------------------------------------
    ASIGNACIÓN DE ROLES 
    ------------------------------------------ */
    //Usamos el semaforo para la modificación del GameState de forma segura

    sem_wait(game_sem); //Tomamos el candado

    //Si ya hay 2 jugadores conectados, rechazamos al tercer
    if(gs-> players_connected >= MAX_PLAYERS){
        sem_post(game_sem); //Liberamos el candado antes de cerrar la conexión
        snprintf(buffer,sizeof(buffer), "%s\n", MSG_ROOM_FULL);
        send(client_fd, buffer, strlen(buffer),0);//Enviamos el mensaje de sala llena  
        printf("[hijo %d] Sala llena, rechazando a %s\n", getpid(),username);
        fflush(stdout);
        close(client_fd); //Cerramos el socket del cliente
        return; //Terminamos la función
    }

    //Asignamos el rol segun orden de llegada y numero de ronda
    //Ronda par: primer jugador setter, Ronda impar: primer jugador guesser
    if(gs->players_connected == 0){
        //Cuando se conecta el primer jugador
        my_role = (gs->round %2 == 0) ? 0 : 1; //Setter es 0, Guesser es 1
        if(my_role == 0){
            gs->setter_fd = client_fd; //Guardamos el file descriptor del setter
        } else {
            gs->guesser_fd = client_fd; //Guardamos el file descriptor del guesser
        }
    }else{
        //Cuando se conecta el segundo jugador
        my_role = (gs->round % 2 == 0) ? 1 : 0; //Setter es 0, Guesser es 1
        if(my_role == 0){
            gs->setter_fd = client_fd; //Guardamos el file descriptor del setter
        } else {
            gs->guesser_fd = client_fd; //Guardamos el file descriptor del guesser
        }
    }

    gs->players_connected++; //Incrementamos el contador de jugadores conectados
    int current_players = gs->players_connected; //Guardamos el numero actual de jugadores para imprimirlo despues de liberar el semaforo

    sem_post(game_sem); //Liberamos el candado

    //Avisamos los roles
    if(my_role == 0){
        snprintf(buffer, sizeof(buffer), "%s:%s\n",MSG_ROLE,ROLE_SETTER);
        printf("[hijo %d] %s es SETTER\n", getpid(),username);
    }else{
        snprintf(buffer, sizeof(buffer), "%s:%s\n", MSG_ROLE, ROLE_GUESSER);
        printf("[hijo %d] %s es GUESSER\n", getpid(),username);
    }

    send(client_fd,buffer,strlen(buffer),0); //Enviamos el mensaje con el rol asignado
    fflush(stdout);

    //Situación cuando solo hay un jugador conectado
    if(current_players < MAX_PLAYERS){
        snprintf(buffer, sizeof(buffer), "%s\n", MSG_WAIT);
        send(client_fd,buffer,strlen(buffer),0); //Enviamos el mensaje de esperar al otro jugador
        printf("[hijo %d] Espereando al segundo jugador...\n",getpid());
        fflush(stdout);

        //Revisamos activamente hasta que se conecte el segundo jugador
        while(gs->players_connected < MAX_PLAYERS){
            usleep(100000); //Revisamos cada 100ms para no saturar la CPU
        }
    }

    /* ------------------------------------------
    LOGICA DEL JUEGO
    ------------------------------------------ */

    // -----------------LOGICA DEL SETTER-------------------------
    if(my_role == 0){

        //Le pedimos la palabra al setter en loop hasta que sea valido
        while(1){
            char word[MAX_WORD];

            snprintf(buffer, sizeof(buffer), "INGRESA_PALABRA\n");
            send(client_fd,buffer,strlen(buffer),0); //Mandamos el mensaje para pedir la palabra

            bytes = recv(client_fd,buffer,sizeof(buffer)-1,0); //Esperamos a que el setter mande la palabra
            if(bytes <= 0) goto disconnect; //Si el cliente se desconecta, vamos a la etiqueta de desconexion
            for(int i = 0; i<bytes; i++){
                if(buffer[i] == '\r') buffer[i] = '\0'; //Quitamos el \r si telnet lo manda
            }

            //Parseamos el mensaje de la palabra
            if(sscanf(buffer, "SET_WORD:%63[^\n]", word)!=1){
                snprintf(buffer,sizeof(buffer), "%s:Formato invalido, usa SET_WORD:PALABRA\n", MSG_ERROR);
                send(client_fd, buffer, strlen(buffer),0); //Enviamos el mensaje de error de formato
                continue; //Volvemos a pedir la palabra
            }

            //Validamos que la palabra sea solo A-Z
            if(!is_valid_word(word)){
                snprintf(buffer,sizeof(buffer), "%s: Solo letras A-Z, sin acentos ni espacios ni n~, min 2 y max %d letras\n", MSG_ERROR, MAX_WORD-1);
                send(client_fd, buffer, strlen(buffer),0); //Enviamos el mensaje de error
                continue; //Volvemos a pedir la palabra
            }

            //Si la palabra es valida, la guardamos en el GameState y construimos el tablero
            sem_wait(game_sem); //Tomamos el candado para modificar el GameState
            set_word(gs,word); //Guardamos la palabra y construimos el tablero
            gs->status = STATE_PLAYING; //Cambiamos el estado a jugando
            sem_post(game_sem); //Liberamos el candado

            //Avisamos al setter que la palabra fue aceptada y el juego va a empezar
            snprintf(buffer, sizeof(buffer),"%s\n",MSG_WAIT);
            send(client_fd,buffer,strlen(buffer),0); //Mandamos el mensaje de esperar al otro jugador
            printf("[hijo %d] Palabra establecida, esperando a que el guesser...\n",getpid());   
            fflush(stdout);
            break; //Salimos del loop de pedir la palabra     
        }

        //El setter espera mientras el guesser adivina
        while(!gs->game_over){
            usleep(200000); //Esperamos 200ms para no saturar la CPU
        }

        //Avisamos al setter el resultado final
        sem_wait(game_sem); //Tomamos el candado para leer el resultado del juego
        if(check_win(gs)){
            snprintf(buffer,sizeof(buffer), "%s:%s\n", MSG_LOSE, gs->word);
        }else{
            snprintf(buffer,sizeof(buffer), "%s:%s\n", MSG_WIN, gs->word);
        }
        sem_post(game_sem); //Liberamos el candado
        send(client_fd, buffer, strlen(buffer),0); //Enviamos el mensaje con el resultado final

    }else{
        // -----------------LOGICA DEL GUESSER-------------------------

        /* NUEVO: Le avisamos al guesser que ya conectaron los 2 jugadores
           y que ahora debe esperar a que el setter ponga la palabra.
           Esto es diferente al WAIT anterior que significaba "espera al segundo jugador" */
        snprintf(buffer, sizeof(buffer), "%s\n", MSG_WAITING_WORD);
        send(client_fd, buffer, strlen(buffer), 0);

        //Esperamos a que el setter establezca la palabra
        while(gs->status != STATE_PLAYING){
            usleep(100000); //Revisamos cada 100ms para no saturar la CPU
        }

        //Mandamos el tablero inicial al guesser
        sem_wait(game_sem); //Tomamos el candado para leer el tablero
        snprintf(buffer,sizeof(buffer), "%s:%s\n", MSG_BOARD, gs->board);
        sem_post(game_sem); //Liberamos el candado
        send(client_fd, buffer, strlen(buffer),0); //Enviamos el tablero inicial

        //Loop principal del guesser para mandar intentos
        while(1){
            char letter;

            //Recibimos el intento del guesser
            bytes = recv(client_fd, buffer, sizeof(buffer)-1,0); //Esperamos a que el guesser mande un intento
            if(bytes <= 0) goto disconnect; //Si el cliente se desconecta, vamos a la etiqueta de desconexion
            buffer[bytes] = '\0'; //Terminamos el string
            for(int i = 0; i<bytes; i++){
                if(buffer[i] == '\r') buffer[i] = '\0'; //Quitamos el \r si telnet lo manda
            }

            //Parseamos el mensaje del intento
            char guess_str[4]; //Para guardar la letra intentada
            if(sscanf(buffer, "GUESS:%3[^\n]", guess_str)!=1 || strlen(guess_str) != 1){
                snprintf(buffer,sizeof(buffer), "%s: Manda solo una letra, ejemplo GUESS:A\n", MSG_ERROR);
                send(client_fd, buffer, strlen(buffer),0); //Enviamos el mensaje de error
                continue; //Volvemos a esperar un intento
            }

            letter = guess_str[0];

            //Validamos que sea una letra valida
            if(!is_valid_letter(letter)){
                snprintf(buffer,sizeof(buffer), "%s: Solo letras A-Z\n", MSG_ERROR);
                send(client_fd, buffer, strlen(buffer),0); //Enviamos el mensaje de error
                continue; //Volvemos a esperar un intento
            }

            //Procesamoe el intento
            sem_wait(game_sem); //Tomamos el candado para modificar el GameState
            int result = process_guess(gs, letter); //Procesamos el intento

            if(result == -1){
                //La letra ya fue intentada antes
                sem_post(game_sem); //Liberamos el candado
                snprintf(buffer,sizeof(buffer), "%s: La letra %c ya fue intentada\n", MSG_ERROR, toupper(letter));
                send(client_fd, buffer, strlen(buffer),0); //Enviamos el mensaje de error
                continue; //Volvemos a esperar un intento
            }

            //Revisamos si gano o perdio
            if(check_win(gs)){
                gs->game_over = 1; //Marcamos que la partida termino
                char word_copy[MAX_WORD];
                strcpy(word_copy, gs->word); //Hacemos una copia de la palabra para enviarla en el mensaje
                sem_post(game_sem); //Liberamos el candado antes de enviar el mensaje
                snprintf(buffer, sizeof(buffer), "%s:%s\n", MSG_WIN, word_copy);
                send(client_fd, buffer, strlen(buffer),0); //Enviamos el mensaje de que gano
                break; //Salimos del loop de intentos
            }

            if(check_lose(gs)){
                gs->game_over = 1; //Marcamos que la partida termino
                char word_copy[MAX_WORD];
                strcpy(word_copy, gs->word); //Hacemos una copia de la palabra para enviarla en el mensaje
                sem_post(game_sem); //Liberamos el candado antes de enviar el mensaje
                snprintf(buffer, sizeof(buffer), "%s:%s\n", MSG_LOSE, word_copy);
                send(client_fd, buffer, strlen(buffer),0); //Enviamos el mensaje de que perdio
                break; //Salimos del loop de intentos
             }

             //Mandamos el resulado del intento
             if(result == 1){
                snprintf(buffer,sizeof(buffer), "%s:%s:%d\n", MSG_CORRECT, gs->board,gs->wrong_attempts);
                send(client_fd, buffer, strlen(buffer),0); //Enviamos el mensaje de que acerto
             }else{
                snprintf(buffer,sizeof(buffer), "%s:%s:%d\n", MSG_WRONG, gs->board,gs->wrong_attempts);
                send(client_fd, buffer, strlen(buffer),0); //Enviamos el mensaje de que fallo
             }

             sem_post(game_sem); //Liberamos el candado
        }
    }

    /* ------------------------------------------
    FIN DE LA PARTIDA 
    ------------------------------------------ */
    //Se hace una preparacion para la siguiente ronda
    sem_wait(game_sem); //Tomamos el candado para modificar el GameState
    gs->players_connected--; //Decrementamos el contador de jugadores conectados
    if(gs->players_connected == 0){
        //El ultimo jugador en irse reinicia el GameState para la siguiente ronda
        gs->round++; //Incrementamos la ronda
        init_game_state(gs); //Reiniciamos el GameState para la siguiente ronda
        printf("[servidor] Ronda %d lista\n", gs->round);
        fflush(stdout);
    }
    sem_post(game_sem); //Liberamos el candado

    //Cerramos el socket del cliente
    disconnect:
        close(client_fd);
        printf("[hijo %d] Conexion cerrada\n", getpid());
        fflush(stdout);
}

/* ------------------------------------------
    MAIN
    ------------------------------------------ */
int main(){
    int server_fd; //Socket del servidor
    int client_fd; //Socket del cliente que se conecta
    struct sockaddr_in server_addr, client_addr; //Direccion del servidor y cliente
    socklen_t client_len = sizeof(client_addr); //Tamaño de la direccion del cliente
    pid_t pid; //PID del proceso

    /* ------------------------------------------
    CARGAMOS A LOS USUARIOS
    ------------------------------------------ */
    if(load_users("users.txt")<0){
        fprintf(stderr, "Error al cargar los usuarios\n");
        exit(1);
    }

    /* ------------------------------------------
    CREAMOS EL GAMESTATE EN MEMORIA COMPARTIDA
    MAP_SHARES para memoria compartida entre procesos
    MAP_ANONYMOUS porque no necesitamos un archivo para la memoria compartida
    PROT_READ | PROT_WRITE para poder leer y escribir en la memoria compartida
    ------------------------------------------ */

    gs = mmap(NULL, sizeof(GameState), PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, -1, 0);
    if(gs == MAP_FAILED){
        perror("Error al crar la memoria compartida");
        exit(1);
    }

    /* ------------------------------------------
    CREAMOS EL SEMAFORO EN MEMORIA COMPARTIDA
    Todo los hijos deben compartir el mismo candado
    pshared=1 significa que es comparido entre procesos
    value = 1 significa que inicia desbloqueado
    ------------------------------------------ */

    game_sem = mmap(NULL, sizeof(sem_t), PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, -1, 0);
    if (game_sem == MAP_FAILED){
        perror("Error al crear el semaforo en memoria compartida");
        exit(1);
    }

    sem_init(game_sem, 1, 1); //Inicializamos el semaforo para que sea compartido entre procesos y que inicie desbloqueado

    /* ------------------------------------------
    INICIALIZAMOS EL GAMESTATE
    ------------------------------------------ */
    init_game_state(gs); //Inicializamos el GameState para la primera ronda
    gs->players_connected = 0; //Aseguramos que el contador de jugadores conectados inicie en 0
    gs->round = 0; //Iniciamos en la ronda 0
    gs->setter_fd = -1; //Inicializamos los file descriptors en -1 para indicar que no hay jugadores conectados
    gs->guesser_fd = -1; //Inicializamos los file descriptors en -1 para indicar que no hay jugadores conectados

    /* ------------------------------------------
    CREAMOS EL SOCKET DEL SERVIDOR
    AF_INET es el IPV4, SOCKET_STREAM es TCP, 0 es el protocolo por defecto para TCP    
    ------------------------------------------ */

    server_fd = socket(AF_INET,SOCK_STREAM,0);
    if(server_fd < 0){
        perror("Error al crear el socket");
        exit(1);
    }

    /*
    SO_REUSEADDR permite reutilizar el puerto inmediatamente después de cerrar el servidor
    Esto es útil para evitar el error "Address already in use" al reiniciar el servidor
    */
   int opt = 1;
   setsockopt(server_fd,SOL_SOCKET,SO_REUSEADDR, &opt, sizeof(opt));

   /*
   CONFIGURAMOS LA DIRECCION DEL SERVIDOR
   INADDR_ANY permite aceptar conexiones en cualquier interfaz de red
   htons convierte el puerto a formato de red
   */
  memset(&server_addr,0,sizeof(server_addr)); //Limpiamos la estructura
  server_addr.sin_family = AF_INET; //IPv4
  server_addr.sin_addr.s_addr = INADDR_ANY; //Aceptar conexiones en cualquier interfaz
  server_addr.sin_port = htons(PORT); //Puerto del servidor

  /*
  ENLACES EL SOCKET DEL SERVIDOR CON LA DIRECCION CONFIGURADA
  */
  if(bind(server_fd,(struct sockaddr *)&server_addr,sizeof(server_addr)) < 0){
        perror("Error al enlazar el socket");
        close(server_fd);
        exit(1);
  }

  /*
  CONFIGURAMOS EL SOCKET DEL SERVIDOR PARA QUE ESCUCHE CONEXIONES
  */
  if(listen(server_fd,5)<0){
        perror("Error al escuchar en el socket");
        close(server_fd);
        exit(1);
  }

  //Instalamos el signal handler para evitar procesos zombies
    signal(SIGCHLD,signal_handler);

  printf("Servidor escuchando en el puerto %d...\n",PORT);
  fflush(stdout);

  /*
  CREAMOS EL LOOP PRINCIPAL DEL SERVIDOR PARA ACEPTAR CONEXIONES
  Para cada cliente que llega, hacemos un fork para crear procesos hijos
  El padre sigue aceptando conexiones mientras los hijos manejan a los clientes
  */
    while(1){
        //Accept bloquea hasta que un cliente se conecta
        client_fd = accept(server_fd,(struct sockaddr*)&client_addr,&client_len);
        if(client_fd < 0){
            perror("Error al aceptar la conexion");
            continue; //Si hay error, seguimos aceptando otras conexiones
        }

        //Hacemos el fok para crear un proceso hijo
        //El hijo retorna 0, el padre retorna el PID del hijo
        pid = fork();

        if(pid < 0){
            perror("Error al hacer fork");
            close(client_fd);
            continue; //Si hay error, seguimos aceptando otras conexiones
        }

        //Logica del proceso hijo
        if(pid == 0){
            //El hijo solo interactua con el cliente, no necesita el socket del servidor
            close(server_fd); //Cerramos el socket del servidor en el hijo
            handle_client(client_fd,client_addr); //Manejamos al cliente
            exit(0); //Terminamos el proceso hijo
        }

        //Logica del proceso padre
        close(client_fd); //El padre no necesita el socket del cliente, lo cierra
    }

    /* ------------------------------------------
    LIMPIEZA DE LA MEMORIA COMPARTIDA Y SEMAFORO
    Tambien terminamos con el socket del servidor
    ------------------------------------------*/
    munmap(gs, sizeof(GameState)); //Liberamos la memoria compartida del GameState
    munmap(game_sem, sizeof(sem_t)); //Liberamos la memoria compartida del
    close(server_fd); //Cerramos el socket del servidor

    return 0;
}