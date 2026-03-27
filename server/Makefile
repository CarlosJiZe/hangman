#Archivo para compilar rapidamente

#Compilador y flags
CC = gcc
#-Wall: muestra todas las advertencias
#-Wextra: muestra advertencias adicionales
#-g: incluye información de depuración
CFLAGS = -Wall -Wextra -g

#Archivos fuente del servidor
SRCS = server.c auth.c game_logic.c

#Nombre del ejecutable final
TARGET = server

#Regla princpal: para compilar todo
all: $(TARGET)

$(TARGET): $(SRCS)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRCS) -lpthread

#lpthread: enlaza la biblioteca de hilos para permitir la concurrencia en el servidor

#Regla para limpiar archivos compilados
clean:
	rm -f $(TARGET) *.o

.PHONY: all clean