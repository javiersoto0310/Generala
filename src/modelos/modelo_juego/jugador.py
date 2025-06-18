class Jugador:
    def __init__(self, nombre):
        self.__nombre = nombre
        self.__puntaje = 0

    def actualizar_puntaje(self, puntos):
        self.__puntaje += puntos

    def obtener_puntaje(self):
        return self.__puntaje

    def obtener_nombre(self):
        return self.__nombre

