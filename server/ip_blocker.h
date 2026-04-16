//Autor Eduardo
//Fecha 7 de abril 2026

#ifndef IP_BLOCKER_H
#define IP_BLOCKER_H

#include <time.h>

#define IP_MAX_ATTEMPTS     5        // intentos antes de bloquear 5
#define BLOCK_DURATION   60      // segundos bloqueada 1 minuto, solo para demostracion
#define MAX_TRACKED_IPS  10      // IPs que toma en consideracion el archivo

typedef struct {
    char   ip[46];               // IPv4 e IPv6
    int    failed_attempts;     //Cuantos intentos lleva fallidos
    time_t first_fail_time;     //Registro del primer error
    time_t block_until;         //Tiempo de bloqueo
    int    is_blocked;          //Estado
} IPRecord;

int  is_ip_blocked(const char *ip);
void record_failed_attempt(const char *ip);
void reset_ip_attempts(const char *ip);
void ip_blocker_init_shared(IPRecord *shared_records, int *shared_count);
int get_failed_attempts(const char *ip);

#endif