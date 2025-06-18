class Turno:
    def __init__(self, jugador: str):
        self.__jugador_actual = jugador
        self.__tiradas_restantes = 3

    def obtener_jugador_actual(self) -> str:
        return self.__jugador_actual

    def obtener_tiradas_restantes(self) -> int:
        return self.__tiradas_restantes

    def disminuir_tiradas_restantes(self):
        if self.__tiradas_restantes > 0:
            self.__tiradas_restantes -= 1

    def reiniciar_tiradas_restantes(self):
        self.__tiradas_restantes = 3

    def reiniciar_turno(self, jugador: str):
        self.__jugador_actual = jugador
        self.reiniciar_tiradas_restantes()
