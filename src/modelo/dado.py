import random

class Dado:
    def __init__(self):
        self.__valor = None

    def lanzar(self):
        self.__valor = random.randint(1, 6)
        return self.__valor

    def obtener_valor(self):
        return self.__valor

    def reiniciar(self):
        self.__valor = None