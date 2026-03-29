# Hangman - Computo Distribuido

Juego multijugador del ahorcado implementado con arquitectura cliente-servidor distribuida. El servidor esta escrito en C con fork para manejo concurrente, y los clientes en Python con tkinter para la interfaz grafica.

---

## Indice

- [Arquitectura](#arquitectura)
- [Requisitos previos](#requisitos-previos)
- [Configuracion del Servidor](#configuracion-del-servidor)
- [Configuracion del Cliente](#configuracion-del-cliente)
- [Modos de Ejecucion](#modos-de-ejecucion)
- [Usuarios de Prueba](#usuarios-de-prueba)
- [Protocolo de Comunicacion](#protocolo-de-comunicacion)

---

## Arquitectura

```
[Cliente Python/tkinter] --TCP--+
                                +---> [Servidor C + fork]
[Cliente Python/tkinter] --TCP--+
```

El servidor corre en un contenedor Docker con Ubuntu y coordina toda la comunicacion. Los clientes corren en cualquier maquina de la red (Mac, Windows, Linux). La comunicacion es por TCP en modo conexion usando mensajes de texto terminados en `\n`.

---

## Requisitos previos

Antes de ejecutar la aplicacion, es necesario contar con lo siguiente:

- Docker Desktop instalado y en ejecucion en la maquina que servira como servidor. Docker Desktop se puede descargar en docker.com y esta disponible para Windows, Mac y Linux.
- Python 3.10 o superior instalado en las maquinas que actuaran como clientes. Python se puede descargar desde python.org.
- Git instalado para clonar el repositorio. Se puede descargar de git-scm.com.
- Todas las maquinas deben estar conectadas a la misma red Wi-Fi si se desea realizar una distribucion real entre dos computadoras distintas.

---

## Paso 1: Configurar el servidor en Docker

El servidor corre en un contenedor de Docker con Ubuntu. La configuracion completa de un contenedor de Docker implica varios pasos adicionales, como la instalacion de Docker Desktop, la descarga de la imagen de Ubuntu, la configuracion de los recursos del contenedor y la gestion de volumenes, que van mas alla del alcance de este documento. Para informacion detallada sobre como configurar Docker desde cero, se recomienda consultar la documentacion oficial en docs.docker.com.

Una vez que el contenedor esta creado, es necesario que el puerto este correctamente mapeado. El mapeo de puertos se realiza con el siguiente comando al momento de crear el contenedor:

```bash
docker run -p 5001:5000 -it ubuntu bash
```

El parametro `-p 5001:5000` indica que el puerto 5001 de la maquina anfitriona apunta al puerto 5000 dentro del contenedor, donde escucha el servidor. Esto permite que los clientes en otras maquinas de la red se conecten al servidor a traves del puerto 5001 de forma transparente.

Si el contenedor ya esta creado con el puerto mapeado, simplemente arrancalo con:

```bash
docker start -i nombre_del_contenedor
```

---

## Paso 2: Instalar dependencias y clonar el repositorio dentro del contenedor

Una vez dentro del contenedor, ejecuta los siguientes comandos uno por uno:

```bash
apt-get update
apt-get install -y git gcc make
git clone https://github.com/CarlosJiZe/hangman.git
cd hangman/server
```

- `apt-get update` actualiza la lista de paquetes disponibles
- `apt-get install -y git gcc make` instala Git para clonar el repositorio, GCC que es el compilador de C, y Make que automatiza la compilacion
- `git clone` descarga el codigo fuente del repositorio
- `cd hangman/server` navega a la carpeta del servidor

---

## Paso 3: Compilar el servidor

Dentro de la carpeta `server`, ejecuta:

```bash
make clean && make
```

Si la compilacion es exitosa, veras algo similar a:
```
gcc -Wall -Wextra -g -o server server.c auth.c game_logic.c -lpthread
```

Si aparece algun error de compilacion, verifica que gcc y make esten instalados correctamente repitiendo el paso anterior.

---

## Paso 4: Arrancar el servidor

```bash
./server
```

Deberias ver:
```
Usuarios cargados: 7
Servidor escuchando en el puerto 5000...
```

El servidor ya esta listo para recibir conexiones. No cierres esta terminal mientras dure la sesion de juego.

---

## Paso 5: Obtener la IP de la maquina donde corre Docker

Para que otros clientes en la red puedan conectarse, necesitas saber la IP de tu maquina. Abre una terminal nueva fuera del contenedor y ejecuta segun tu sistema operativo:

En Mac:
```bash
ipconfig getifaddr en0
```

En Linux:
```bash
hostname -I
```

En Windows, abre cmd o PowerShell y ejecuta:
```bash
ipconfig
```

Busca la seccion correspondiente a tu adaptador Wi-Fi y anota el valor que aparece junto a "Direccion IPv4". Tendra un formato similar a `192.168.1.110`.

---

## Paso 6: Configurar y ejecutar el cliente

En cada maquina que vaya a jugar, abre una terminal y clona el repositorio:

```bash
git clone https://github.com/CarlosJiZe/hangman.git
cd hangman/client
```

En Windows usa `cd hangman\client` con diagonal invertida.

Antes de correr el cliente, verifica que Python esta correctamente instalado:

En Mac:
```bash
python3 --version
```

Si tienes varias versiones de Python en Mac, usa el comando especifico de la version que instalaste, por ejemplo, `python3.12 --version`. Se recomienda instalar Python 3.12 desde python.org o con Homebrew para evitar conflictos con el Python del sistema.

En Windows:
```bash
python --version
```

En Linux:
```bash
python3 --version
```

Tambien verifica que tkinter este disponible ejecutando:

En Mac:
```bash
python3.12 -m tkinter
```

En Windows y Linux:
```bash
python -m tkinter
```

Si se abre una pequena ventana de prueba, tkinter esta listo. Si no, en Mac instalalo con:
```bash
brew install python-tk@3.12
```

En Linux:
```bash
apt-get install python3-tk
```

En Windows, tkinter viene incluido con la instalacion estandar de Python desde python.org.

---

## Paso 7: Ejecutar el cliente

El cliente recibe como argumentos la IP del servidor y el puerto. El formato es:

```bash
python3.12 main.py <IP_DEL_SERVIDOR> <PUERTO>
```

Si el cliente corre en la misma maquina que el servidor:

```bash
python3.12 main.py localhost 5001
```

Si el cliente corre en una maquina diferente (sustituye por la IP obtenida en el Paso 5):

En Mac o Linux:
```bash
python3.12 main.py 192.168.1.110 5001
```

En Windows:
```bash
python main.py 192.168.1.110 5001
```

Repite este paso en la segunda maquina para el segundo jugador. Ambas maquinas deben estar en la misma red Wi-Fi.

---

## Paso 8: Jugar

Si se hizo todo lo anterior correctamente, se deben desplegar las pantallas de juego en las que se inicia sesion, y dentro de la propia aplicacion existen instrucciones especificas de como jugar.

---

## Usuarios de Prueba

Los siguientes usuarios estan registrados en `server/users.txt`:

| Usuario  | Contrasena |
|----------|------------|
| carlos   | 1234       |
| omar     | 4321       |
| padrino  | 0000       |
| marco    | 5678       |
| ana      | abcd       |
| luis     | pass1      |
| sofia    | qwerty     |

---

## Protocolo de Comunicacion

Todos los mensajes son strings de texto terminados en `\n` con el formato `COMANDO:arg1:arg2\n`.

| Mensaje | Direccion | Descripcion |
|---------|-----------|-------------|
| `LOGIN:user:pass` | Cliente a Servidor | Autenticacion |
| `LOGIN_OK` | Servidor a Cliente | Login exitoso |
| `LOGIN_FAIL` | Servidor a Cliente | Login fallido |
| `ROLE:SETTER` | Servidor a Cliente | Asignacion de rol |
| `ROLE:GUESSER` | Servidor a Cliente | Asignacion de rol |
| `SET_WORD:PALABRA` | Cliente a Servidor | Setter pone la palabra |
| `GUESS:A` | Cliente a Servidor | Guesser adivina una letra |
| `CORRECT:tablero:intentos` | Servidor a Cliente | Letra correcta |
| `WRONG:tablero:intentos` | Servidor a Cliente | Letra incorrecta |
| `WIN:PALABRA` | Servidor a Cliente | Juego terminado, gano |
| `LOSE:PALABRA` | Servidor a Cliente | Juego terminado, perdio |
| `ROOM_FULL` | Servidor a Cliente | Sala llena |

---

## Equipo

Ingenieria en Sistemas y Graficas Computacionales
Universidad Panamericana Guadalajara

- Carlos J. Zepeda
- Jose M. Paredes
- Omar S. Lopez

CDS: Computo Distribuido
Dr. Juan L. Pimentel
