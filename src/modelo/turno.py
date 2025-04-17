import logging
from modelo.puntaje import Puntaje
from modelo.tiempo import Tiempo

class Turno:
    def __init__(self, jugador: str):
        self.__jugador_actual = jugador
        self.__tiradas_restantes = 3
        self.__tiempo = Tiempo()

    def obtener_jugador_actual(self) -> str:
        return self.__jugador_actual

    def obtener_tiradas_restantes(self) -> int:
        return self.__tiradas_restantes

    def disminuir_tiradas_restantes(self):
        if self.__tiradas_restantes > 0:
            self.__tiradas_restantes -= 1

    def reiniciar_tiradas_restantes(self):
        self.__tiradas_restantes = 3
        logging.info(f"Tiradas restantes reiniciadas para {self.__jugador_actual}.")

    def obtener_tiempo_restante(self) -> int:
        return self.__tiempo.obtener_tiempo_restante()

    def disminuir_tiempo(self) -> int:
        return self.__tiempo.disminuir_tiempo()

    def tiempo_agotado(self) -> bool:
        return self.__tiempo.tiempo_agotado()

    def reiniciar_turno(self, jugador: str):
        self.__jugador_actual = jugador
        self.reiniciar_tiradas_restantes()
        self.__tiempo.reiniciar_tiempo()
        logging.info(f"Turno reiniciado para {jugador}.")

    def pasar_turno_si_el_tiempo_se_agotado(self, puntaje: Puntaje, actualizar_tabla_puntajes):
        categoria = puntaje.encontrar_primer_categoria_no_completada(self.__jugador_actual)
        if categoria:
            puntaje.registrar_puntos(self.__jugador_actual, 0, categoria)
            logging.info(f"Tiempo agotado. Asignados 0 puntos a {categoria} para {self.__jugador_actual}.")
            actualizar_tabla_puntajes()
        else:
            logging.info(f"Tiempo agotado. Todas las categorías están completadas para {self.__jugador_actual}.")
