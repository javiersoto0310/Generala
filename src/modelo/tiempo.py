class Tiempo:
    def __init__(self, tiempo_inicial: int = 45):
        self.__tiempo = tiempo_inicial

    def obtener_tiempo_restante(self) -> int:
        return self.__tiempo

    def disminuir_tiempo(self) -> int:
        if self.__tiempo > 0:
            self.__tiempo -= 1
        return self.__tiempo

    def reiniciar_tiempo(self, tiempo_inicial: int = 45):
        self.__tiempo = tiempo_inicial

    def tiempo_agotado(self) -> bool:
        return self.__tiempo <= 0