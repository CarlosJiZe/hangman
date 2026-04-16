//Autor Eduardo
//Fecha 4 de abril 2026
//La intentcion de este codigo es loggear los accesos al servidor

#include <stdio.h>
#include <time.h>
#include "logger.h"

void log_auth_attempt(const char *ip, const char *username,
                      AuthResult result, int attempt_count) {
    FILE *log;
    time_t now = time(NULL);
    char   timestamp[20];
    struct tm *tm_info = localtime(&now);

    strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", tm_info);

    log = fopen(LOG_FILE, "a");          /* append */
    if (log == NULL) {
        perror("No se pudo abrir el log");
        return;
    }

    const char *result_str =
        (result == AUTH_SUCCESS) ? "SUCCESS" :
        (result == AUTH_BLOCKED) ? "BLOCKED" : "FAILURE";

    fprintf(log, "[%s] IP=%-15s USER=%-20s RESULT=%-7s ATTEMPT=%d\n",
            timestamp, ip, username, result_str, attempt_count);

    fclose(log);
}