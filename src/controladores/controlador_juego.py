from PySide6.QtCore import QObject, Signal
from typing import List, Optional

from modelo.jugador import Jugador
from modelo.turno import Turno
import logging

logging.basicConfig(level=logging.INFO)

class ControladorJuego(QObject):
    turno_actual_cambiado = Signal(str)

    def __init__(self):
        super().__init__()
        self.turno: Optional[Turno] = None
        self.jugadores: List[Jugador] = []
        self.jugador_actual: Optional[Jugador] = None
        self.indice_jugador_actual: int = 0

    def iniciar_partida(self, nombres_jugadores: List[str], nombre_local: str):
        logging.info(f"Iniciando partida con jugadores: {nombres_jugadores}, jugador local: {nombre_local}")
        self.jugadores = []
        self.jugador_actual = None
        for nombre in nombres_jugadores:
            jugador = Jugador(nombre)
            self.jugadores.append(jugador)
            if nombre == nombre_local:
                self.jugador_actual = jugador

        if self.jugador_actual:
            self.turno = Turno(self.jugador_actual.obtener_nombre())
            self.indice_jugador_actual = self.jugadores.index(self.jugador_actual)
            logging.info(
                f"Jugadores locales creados: {[j.obtener_nombre() for j in self.jugadores]}, turno inicial: {self.turno.obtener_jugador_actual()}")
            self.turno_actual_cambiado.emit(self.turno.obtener_jugador_actual())
        else:
            logging.error("No se pudo determinar el jugador local.")

    def pasar_turno(self):
        if self.jugadores:
            self.indice_jugador_actual = (self.indice_jugador_actual + 1) % len(self.jugadores)
            nuevo_jugador = self.jugadores[self.indice_jugador_actual]
            self.turno.reiniciar_turno(nuevo_jugador.obtener_nombre())
            logging.info(f"El turno ha pasado a {self.turno.obtener_jugador_actual()}.")
            self.turno_actual_cambiado.emit(self.turno.obtener_jugador_actual())




