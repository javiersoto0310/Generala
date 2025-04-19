from PySide6.QtCore import QObject, Signal
from typing import List, Optional

from modelo.jugador import Jugador
from modelo.turno import Turno
from modelo.dado import Dado
import logging
import socketio

logging.basicConfig(level=logging.INFO)

class ControladorJuego(QObject):
    turno_actual_cambiado = Signal(str)
    habilitar_lanzamiento = Signal()
    deshabilitar_lanzamiento = Signal()
    mostrar_resultados_lanzamiento = Signal(str, list)

    def __init__(self):
        super().__init__()
        self.turno: Optional[Turno] = None
        self.jugadores: List[Jugador] = []
        self.jugador_actual: Optional[Jugador] = None
        self.indice_jugador_actual: int = 0
        self.puede_lanzar: bool = False
        self.sala_id_actual: Optional[str] = None
        self.cliente: Optional[socketio.Client] = None

    def set_cliente(self, cliente: socketio.Client):
        self.cliente = cliente

    def iniciar_partida(self, nombres_jugadores: List[str], nombre_local: str, sala_id: Optional[str] = None, primer_jugador: Optional[str] = None):
        logging.info(f"Valor de primer_jugador recibido: {primer_jugador}")
        logging.info(f"Iniciando partida en sala: {sala_id} con jugadores: {nombres_jugadores}, jugador local: {nombre_local}, primer jugador: {primer_jugador}")
        self.jugadores = []
        self.jugador_actual = None
        self.sala_id_actual = sala_id
        self.puede_lanzar = False

        for nombre in nombres_jugadores:
            jugador = Jugador(nombre)
            self.jugadores.append(jugador)
            if nombre == nombre_local:
                self.jugador_actual = jugador

        if self.jugador_actual:
            self.turno = Turno(primer_jugador)
            self.indice_jugador_actual = self.jugadores.index(self.jugador_actual)
            logging.info(f"Jugadores locales creados: {[j.obtener_nombre() for j in self.jugadores]}, turno inicial: {self.turno.obtener_jugador_actual()}")
            logging.info(f"Turno inicial: {self.turno.obtener_jugador_actual()}")

            self.turno_actual_cambiado.emit(primer_jugador)

            if primer_jugador == nombre_local:
                logging.info(f"ControladorJuego - Habilitando lanzamiento para: {nombre_local} (primer jugador: {primer_jugador})")
                self.puede_lanzar = True
                self.habilitar_lanzamiento.emit()
            else:
                logging.info(f"ControladorJuego - Deshabilitando lanzamiento para: {nombre_local} (primer jugador: {primer_jugador})")
                self.puede_lanzar = False
                self.deshabilitar_lanzamiento.emit()
        else:
            logging.error("No se pudo determinar el jugador local.")

    def lanzar_dados(self):
        if self.puede_lanzar and self.jugador_actual and self.turno.obtener_jugador_actual() == self.jugador_actual.obtener_nombre() and self.cliente:
            dados_lanzados = [Dado().lanzar() for _ in range(5)]
            logging.info(f"{self.jugador_actual.obtener_nombre()} ha lanzado los dados: {dados_lanzados}")
            self.cliente.emit('lanzar_dados', {'sala_id': self.sala_id_actual, 'resultados': dados_lanzados})
            self.puede_lanzar = False
            self.deshabilitar_lanzamiento.emit()
        elif not self.puede_lanzar:
            logging.warning("No es el turno para lanzar los dados o ya has lanzado.")
        elif self.jugador_actual and self.turno.obtener_jugador_actual() != self.jugador_actual.obtener_nombre():
            logging.warning("No es el turno del jugador local para lanzar.")
        else:
            logging.error("Error al intentar lanzar los dados: jugador actual no definido o cliente no conectado.")

    def pasar_turno(self):
        if self.jugadores:
            self.indice_jugador_actual = (self.indice_jugador_actual + 1) % len(self.jugadores)
            nuevo_jugador = self.jugadores[self.indice_jugador_actual]
            self.turno.reiniciar_turno(nuevo_jugador.obtener_nombre())
            logging.info(f"Reiniciando turno para el jugador: {nuevo_jugador.obtener_nombre()}")

            self.turno_actual_cambiado.emit(self.turno.obtener_jugador_actual())
            logging.info(f"Emitida señal turno_actual_cambiado con jugador: {self.turno.obtener_jugador_actual()}")

            if nuevo_jugador.obtener_nombre() == self.jugador_actual.obtener_nombre():
                self.puede_lanzar = True
                logging.info(f"Habilitando botón de lanzamiento para el jugador local: {nuevo_jugador.obtener_nombre()}")
                self.habilitar_lanzamiento.emit()
            else:
                logging.info(f"El jugador local no tiene el turno: {self.jugador_actual.obtener_nombre()}")

    def recibir_resultados_lanzamiento(self, jugador_sid, resultados):
        logging.info(f"Resultados del lanzamiento del jugador {jugador_sid}: {resultados}")
        self.mostrar_resultados_lanzamiento.emit(jugador_sid, resultados)





