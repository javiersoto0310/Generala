# Generala en Red

## Objetivo del juego

El objetivo del juego es obtener la mayor cantidad de puntos posible al completar diferentes combinaciones con los cinco dados, compitiendo contra otro jugador a través de la red.

## Reglas del juego

- **Turnos:** Los jugadores se turnan para lanzar los dados. El orden de los turnos se determina una vez que los jugadores se unen a la sala de juego, comenzando por quien creó la sala.
- **Lanzamientos:**
  * En cada turno, el jugador tiene hasta tres oportunidades para lanzar los dados.
  * En el primer lanzamiento, se lanzan los cinco dados.
  * Después del primer lanzamiento, el jugador puede elegir qué dados conservar y cuáles volver a lanzar.
  * El jugador puede optar por no realizar el segundo o tercer lanzamiento si está satisfecho con su resultado.
- **Combinaciones:** El jugador debe intentar obtener alguna de las siguientes combinaciones:
  * Unos, dos, tres, cuatro, cinco y seis: Se suma el valor total de los dados que coinciden con el número elegido.
  * Escalera: Secuencia de cinco números consecutivos (1-2-3-4-5 o 2-3-4-5-6).
  * Full: Tres dados con el mismo número y dos dados con otro número igual entre ellos.
  * Póker: Cuatro dados con el mismo número.
  * Generala: Cinco dados con el mismo número.
  * Generala doble: Dos generalas en la misma partida.
- **Puntuación:**
  * Cada combinación tiene un valor de puntuación diferente:
    * Uno: Suma de todos los dados con valor 1.
    * Dos: Suma de todos los dados con valor 2.
    * Tres: Suma de todos los dados con valor 3.
    * Cuatro: Suma de todos los dados con valor 4.
    * Cinco: Suma de todos los dados con valor 5.
    * Seis: Suma de todos los dados con valor 6.
    * Escalera: 20 puntos.
    * Full: 30 puntos.
    * Póker: 40 puntos.
    * Generala: 50 puntos.
    * Generala doble: 100 puntos.
- **Juego en Red:**
  * Un jugador inicia una sala de juego.
  * Otros jugadores (clientes) pueden listar las salas disponibles y unirse a una de ellas.
  * Solo pueden jugar dos jugadores por sala.
  * Los turnos se suceden entre los jugadores conectados a la misma sala.
  * El ganador se determina al finalizar la partida, basándose en la mayor cantidad de puntos acumulados por cada jugador.
- **Fin del juego:**
  * El juego finaliza cuando los jugadores en la sala han completado todas las categorías.
  * El jugador con la mayor cantidad de puntos es el ganador de la partida en red.

## Cómo ejecutar el proyecto

Antes de comenzar, necesitarás abrir varias **terminales** o **líneas de comandos** en tu computadora. Aquí te explico cómo hacerlo en los sistemas operativos más comunes:

* **En Windows:**
    1.  Presiona la tecla de **Windows** en tu teclado.
    2.  Escribe `cmd` y presiona **Enter**. Esto abrirá la ventana del Símbolo del sistema (CMD).
    3.  Alternativamente, puedes buscar "Símbolo del sistema" en el menú de inicio.

* **En Linux:**
    1.  La forma de abrir la terminal puede variar según la distribución. Generalmente, puedes encontrarla buscando "Terminal" en el menú de aplicaciones o usando una combinación de teclas como Ctrl + Alt + T.

Una vez que tengas las terminales abiertas, sigue estos pasos:

1.  **Clonar el repositorio desde GitHub:**
    * Usa el siguiente comando para descargar el código del juego:
        ```bash
        git clone [https://github.com/javiersoto0310/Generala.git](https://github.com/javiersoto0310/Generala.git)
        ```
    * Una vez que se complete la descarga, navega a la carpeta del proyecto usando el comando:
        ```bash
        cd Generala
        ```

2.  **Instalar Python y pip (si no los tienes instalados):**
    * Para ejecutar este juego, necesitarás tener instalado **Python** en tu computadora. `pip` es un programa que viene con Python y nos permite instalar otras herramientas necesarias. Si no tienes Python instalado, puedes descargarlo desde el sitio web oficial: [https://www.python.org/downloads/](https://www.python.org/downloads/). Asegúrate de marcar la opción para agregar Python al PATH durante la instalación.

3.  **Instalar pip-tools:**
    * `pip-tools` es una herramienta que nos ayudará a gestionar las librerías que necesita el juego. Para instalarlo, usa el siguiente comando en la terminal:
        ```bash
        pip install pip-tools
        ```

4.  **Crear un entorno virtual (recomendado):**
    * Crear un **entorno virtual** es una práctica recomendada en Python para aislar las dependencias de este proyecto de otros proyectos que puedas tener en tu computadora. Esto evita posibles conflictos entre librerías. Para crear uno, usa el siguiente comando:
        ```bash
        python3 -m venv venv
        ```
    * Esto creará una carpeta llamada "venv" dentro de tu proyecto.

5.  **Activar el entorno virtual:**
    * Antes de instalar las dependencias del juego, debes activar el entorno virtual. El comando para activarlo depende de tu sistema operativo:
        * **En Windows:**
            ```bash
            venv\Scripts\activate
            ```
        * **En Linux:**
            ```bash
            source venv/bin/activate
            ```
    * Una vez activado, verás el nombre del entorno virtual (`(venv)`) al principio de la línea de comandos.

6.  **Compilar e instalar las dependencias del juego:**
    * El juego necesita algunas librerías para funcionar correctamente. Estas se definen en el archivo `requirements.in`. Primero, debes **compilar** este archivo para generar el archivo `requirements.txt` que contiene las versiones específicas de las librerías. Ejecuta el siguiente comando:
        ```bash
        pip-compile requirements.in
        ```
    * Una vez que se haya generado el archivo `requirements.txt`, puedes instalar las dependencias usando el siguiente comando:
        ```bash
        pip install -r requirements.txt
        ```

7.  **Ejecutar el juego en red:**
    * **Iniciar el Servidor:**
        * Abre una **nueva** ventana de terminal o línea de comandos.
        * Navega a la carpeta `src/red` dentro del directorio de tu proyecto Generala:
            ```bash
            cd Generala/src/red
            ```
        * Ejecuta el archivo del servidor para iniciar la funcionalidad de red del juego:
            ```bash
            python servidor.py
            ```
        * Deja esta ventana de terminal abierta. El servidor estará en funcionamiento y listo para aceptar conexiones de los clientes.

    * **Iniciar los Clientes (Jugadores):**
        * Abre **dos ventanas de terminal o línea de comandos adicionales**.

        * **Primer Cliente (Creación de la Sala):**
            * En la primera de estas nuevas ventanas, navega al directorio raíz de tu proyecto Generala:
                ```bash
                cd Generala
                ```
            * Ejecuta el archivo principal del juego para iniciar el primer cliente. Este cliente será el encargado de crear la sala de juego:
                ```bash
                python main.py
                ```

        * **Segundo Cliente (Unirse a la Sala):**
            * En la segunda de estas nuevas ventanas, navega también al directorio raíz de tu proyecto Generala:
                ```bash
                cd Generala
                ```
            * Ejecuta el archivo principal del juego para iniciar el segundo cliente. Este cliente deberá listar las salas disponibles y unirse a la creada por el primer cliente:
                ```bash
                python main.py
                ```

    * **Comenzar a Jugar:**
        * Una vez que ambos clientes estén conectados a la misma sala, el juego comenzará.
        * **El jugador que creó la sala será el primero en realizar su turno.**
        * Sigue las instrucciones que aparecerán en la interfaz de cada cliente para lanzar los dados, seleccionar qué dados conservar y completar las combinaciones.
      