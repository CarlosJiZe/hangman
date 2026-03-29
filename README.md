# Hangman - Computo Distribuido

Juego multijugador del ahorcado implementado con arquitectura cliente-servidor distribuida. El servidor esta escrito en C con fork para manejo concurrente, y los clientes en Python con tkinter para la interfaz grafica.

---

## Indice

- [Arquitectura](#arquitectura)
- [Requisitos](#requisitos)
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

## Requisitos

### Servidor
- Docker Desktop instalado
- Imagen de Ubuntu en Docker

### Cliente
- Python 3.10 o superior con tkinter incluido
  - En Mac: se recomienda instalar Python 3.12 desde python.org o con Homebrew, ya que el Python del sistema puede ser una version antigua
  - En Windows: cualquier instalacion de Python desde python.org, Miniforge o Anaconda funciona
  - En Linux: instalar `python3` y `python3-tk` con el gestor de paquetes

---

## Configuracion del Servidor

### 1. Levantar el contenedor Docker

Si ya tienes el contenedor creado con el puerto mapeado:
```bash
docker start -i ubuntu1
```

Si es la primera vez, crea el contenedor mapeando el puerto:
```bash
docker run -p 5001:5000 -it ubuntu bash
```

El mapeo `5001:5000` significa que el puerto 5001 de tu maquina apunta al puerto 5000 del contenedor donde escucha el servidor.

### 2. Clonar el repositorio dentro del contenedor

```bash
apt-get update && apt-get install -y git gcc make
git clone https://github.com/CarlosJiZe/hangman.git
cd hangman/server
```

### 3. Compilar el servidor

```bash
make
```

Si compila correctamente veras:
```
gcc -Wall -Wextra -g -o server server.c auth.c game_logic.c -lpthread
```

### 4. Arrancar el servidor

```bash
./server
```

Deberias ver:
```
Usuarios cargados: 7
Servidor escuchando en el puerto 5000...
```

---

## Configuracion del Cliente

### Paso 1 - Clonar el repositorio

En Mac o Linux:
```bash
git clone https://github.com/CarlosJiZe/hangman.git
cd hangman/client
```

En Windows (abre PowerShell o cmd):
```bash
git clone https://github.com/CarlosJiZe/hangman.git
cd hangman\client
```

Si no tienes git instalado, descarga el ZIP directamente desde GitHub con el boton verde "Code" y descomprimelo.

### Paso 2 - Verificar que Python funciona

En Mac, es posible que tengas varias versiones de Python instaladas. Verifica cual tienes disponible:
```bash
python3 --version
python3.12 --version
```

Usa el comando que te devuelva una version 3.10 o superior. En esta guia usamos `python3.12` para Mac pero sustituye por el comando que funcione en tu caso.

En Windows:
```bash
python --version
```

Debes ver Python 3.10 o superior. Si no lo tienes instalado, descargalo desde python.org.

### Paso 3 - Verificar que tkinter esta instalado

```bash
# En Mac
python3.12 -m tkinter

# En Windows
python -m tkinter
```

Si se abre una ventanita pequeña, tkinter esta listo. Si da error en Mac, instala Python con tkinter incluido:
```bash
brew install python-tk@3.12
```

---

## Modos de Ejecucion

### Modo 1 - Dos clientes en localhost

Ambos clientes se conectan al servidor que corre en Docker en la misma maquina.

Terminal 1 - Servidor (dentro del contenedor Docker):
```bash
./server
```

Terminal 2 - Cliente 1 (en Mac):
```bash
python3.12 main.py localhost 5001
```

Terminal 3 - Cliente 2 (en Mac):
```bash
python3.12 main.py localhost 5001
```

En Windows usa `python` en lugar de `python3.12`.

---

### Modo 2 - Distribucion real (dos maquinas distintas)

El servidor corre en Docker en una maquina y los clientes en maquinas diferentes de la misma red WiFi.

Paso 1 - Obtener la IP de la maquina donde corre Docker:

En Mac:
```bash
ipconfig getifaddr en0
```

En Linux:
```bash
hostname -I
```

En Windows (abre cmd o PowerShell):
```bash
ipconfig
```
Busca la seccion de tu adaptador WiFi y anota el valor de `Direccion IPv4`. Se ve algo asi: `192.168.1.110`

Paso 2 - Arrancar el servidor dentro del contenedor:
```bash
./server
```

Paso 3 - Cliente en la misma maquina que el servidor (Mac):
```bash
python3.12 main.py localhost 5001
```

Paso 4 - Cliente en otra maquina de la red:

En Mac:
```bash
python3.12 main.py 192.168.1.110 5001
```

En Windows:
```bash
python main.py 192.168.1.110 5001
```

Sustituye `192.168.1.110` por la IP que obtuviste en el Paso 1. Ambas maquinas deben estar en la misma red WiFi.

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
