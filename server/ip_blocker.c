//Autor Eduardo
//Fecha 7 de abril 2026
//La intentcion de este codigo es poner una capa de seguridad pequeña, para evitar que manden muchas solicitudes

#include <stdio.h>
#include <string.h>
#include <time.h>
#include "ip_blocker.h"

//Punteros a los registros de intento de acceso
static IPRecord *ip_records  = NULL;
static int      *num_tracked = NULL;

void ip_blocker_init_shared(IPRecord *shared_records, int *shared_count){
    ip_records  = shared_records;
    num_tracked = shared_count;
}

/* Busca o crea un registro para la IP */
static IPRecord *get_or_create_record(const char *ip) {
    int i;
    time_t now = time(NULL);

    for (i = 0; i < *num_tracked; i++) {
        if (strcmp(ip_records[i].ip, ip) == 0) {
            /* Expiró el bloqueo: limpiar */
            if (ip_records[i].is_blocked && now >= ip_records[i].block_until) {
                ip_records[i].is_blocked       = 0;
                ip_records[i].failed_attempts  = 0;
                ip_records[i].first_fail_time  = 0;
            }
            return &ip_records[i];
        }
    }

    if (*num_tracked >= MAX_TRACKED_IPS)
        return NULL;          /* tabla llena */

    /* Nuevo registro */
    memset(&ip_records[*num_tracked], 0, sizeof(IPRecord));
    strncpy(ip_records[*num_tracked].ip, ip, sizeof(ip_records[0].ip) - 1);
    return &ip_records[(*num_tracked)++];
}

/* Retorna 1 si la IP está bloqueada, 0 si no */
int is_ip_blocked(const char *ip) {
    IPRecord *rec = get_or_create_record(ip);
    if (rec == NULL) return 0;
    return rec->is_blocked;
}

/* Registra un intento fallido; bloquea si alcanza el límite */
void record_failed_attempt(const char *ip) {
    IPRecord *rec = get_or_create_record(ip);
    if (rec == NULL) return;

    time_t now = time(NULL);
    if (rec->first_fail_time == 0)
        rec->first_fail_time = now;

    rec->failed_attempts++;

    if (rec->failed_attempts >= IP_MAX_ATTEMPTS) {
        rec->is_blocked   = 1;
        rec->block_until  = now + BLOCK_DURATION;
        fprintf(stderr,
            "[BLOQUEADA] IP %s bloqueada por %d segundos (intentos: %d)\n",
            ip, BLOCK_DURATION, rec->failed_attempts);
    }
}

/* Limpia el contador tras un login exitoso */
void reset_ip_attempts(const char *ip) {
    IPRecord *rec = get_or_create_record(ip);
    if (rec == NULL) return;
    rec->failed_attempts = 0;
    rec->is_blocked      = 0;
    rec->first_fail_time = 0;
}

int get_failed_attempts(const char *ip) {
    IPRecord *rec = get_or_create_record(ip);
    if (rec == NULL) return 0;
    return rec->failed_attempts;
}