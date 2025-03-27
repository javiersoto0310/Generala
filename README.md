# Generala

## Objetivo del juego

El objetivo del juego es obtener la mayor cantidad de puntos posible al completar diferentes combinaciones con los cinco dados.

## Reglas del juego

- **Turnos:** Los jugadores se turnan para lanzar los dados.
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
- **Fin del juego:**
  * El juego finaliza cuando los jugadores han completado todas las categorías.
  * El jugador con la mayor cantidad de puntos es el ganador.

## Cómo ejecutar el proyecto

1. **Abre la terminal o línea de comandos:**
   * En Windows, puedes buscar "cmd" o "PowerShell" en el menú de inicio.
   * En macOS y Linux, puedes abrir la aplicación "Terminal".

2. **Navega al directorio del proyecto:**
   * Usa el comando `cd` (change directory) para ir a la carpeta donde clonaste el repositorio. Por ejemplo, si clonaste el repositorio en una carpeta llamada "generala", escribe:
     ```bash
     cd generala
     ```

3. **Crea un entorno virtual:**
   * Un entorno virtual es como una "caja" donde se instalan las dependencias del proyecto, aislándolas de otros proyectos.
   * Para crear un entorno virtual, usa el siguiente comando:
     ```bash
     python3 -m venv venv
     ```
   * Esto creará una carpeta llamada "venv" dentro de tu proyecto.

4. **Activa el entorno virtual:**
   * Antes de instalar las dependencias, debes "activar" el entorno virtual.
   * En Windows, usa este comando:
     ```bash
     venv\Scripts\activate
     ```
   * En macOS y Linux, usa este comando:
     ```bash
     source venv/bin/activate
     ```
   * Verás que el nombre del entorno virtual ("venv") aparece al principio de la línea de comandos, indicando que está activado.

5. **Instala las dependencias:**
   * Ahora, instala las bibliotecas necesarias para que el juego funcione. Usa el siguiente comando:
     ```bash
     pip install -r requirements.txt
     ```
   * Este comando leerá el archivo `requirements.txt` e instalará todas las dependencias necesarias.

6. **Ejecuta el juego:**
   * Finalmente, ejecuta el juego usando el siguiente comando:
     ```bash
     python main.py
     ```
   * ¡El juego debería abrirse!

## Archivos adicionales necesarios

Este proyecto utiliza la biblioteca **PySide6**, que incluye el archivo binario `libQt6WebEngineCore.so.6`. Este archivo es esencial para ejecutar el programa. Sin embargo, debido a su tamaño, no está incluido directamente en el repositorio.

### Cómo obtener el archivo:
1. Asegúrate de instalar las dependencias del proyecto desde el archivo `requirements.txt`:
   ```bash
   pip install -r requirements.txt

