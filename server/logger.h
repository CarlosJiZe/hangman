#ifndef LOGGER_H
#define LOGGER_H

#define LOG_FILE "auth_log.txt"

typedef enum {
    AUTH_SUCCESS,
    AUTH_FAILURE,
    AUTH_BLOCKED        /* intento desde IP bloqueada */
} AuthResult;

void log_auth_attempt(const char *ip, const char *username,
                      AuthResult result, int attempt_count);

#endif