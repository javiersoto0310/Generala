import uuid

class Jugador:
    def __init__(self, nombre):
        self.__id = str(uuid.uuid4())[:8]
        self.__nombre = nombre
        self.__puntaje = 0

    def actualizar_puntaje(self, puntos):
        self.__puntaje += puntos

    def obtener_puntaje(self):
        return self.__puntaje

    def obtener_nombre(self):
        return self.__nombre

    def obtener_id(self):
        return self.__id

    def __str__(self):
        return f"Jugador(ID: {self.__id}, Nombre: {self.__nombre}, Puntaje: {self.__puntaje})"