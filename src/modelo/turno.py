import logging
from modelo.puntaje import Puntaje

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

    def pasar_turno_por_tiempo_agotado(self, puntaje: Puntaje, actualizar_tabla_puntajes):
        categoria = puntaje.encontrar_primer_categoria_no_completada(self.__jugador_actual)
        if categoria:
            puntaje.registrar_puntos(self.__jugador_actual, 0, categoria)
            logging.info(f"Tiempo agotado. Se asignaron 0 puntos en '{categoria}' a {self.__jugador_actual}.")
            actualizar_tabla_puntajes()
        else:
            logging.info(f"{self.__jugador_actual} ya completó todas las categorías.")
