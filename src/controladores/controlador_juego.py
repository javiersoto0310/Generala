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
    actualizar_tiradas_restantes = Signal(int)  # Nueva señal

    def __init__(self):
        super().__init__()
        self.turno: Optional[Turno] = None
        self.jugadores: List[Jugador] = []
        self.jugador_actual: Optional[Jugador] = None
        self.indice_jugador_actual: int = 0
        self.puede_lanzar: bool = False
        self.sala_id_actual: Optional[str] = None
        self.cliente: Optional[socketio.Client] = None
        self.tiradas_restantes: int = 0
        self.dados_actuales: List[Optional[int]] = [None] * 5
        self.dados_bloqueados: List[bool] = [False] * 5

    def set_cliente(self, cliente: socketio.Client):
        self.cliente = cliente

    def iniciar_partida(self, nombres_jugadores: List[str], nombre_local: str, sala_id: Optional[str] = None, primer_jugador: Optional[str] = None):
        logging.info(f"Valor de primer_jugador recibido: {primer_jugador}")
        logging.info(f"Iniciando partida en sala: {sala_id} con jugadores: {nombres_jugadores}, jugador local: {nombre_local}, primer jugador: {primer_jugador}")
        self.jugadores = []
        self.jugador_actual = None
        self.sala_id_actual = sala_id
        self.puede_lanzar = False
        self.resetear_tiradas()  

        for nombre in nombres_jugadores:
            jugador = Jugador(nombre)
            self.jugadores.append(jugador)
            if nombre == nombre_local:
                self.jugador_actual = jugador

        if self.jugador_actual:
            self.turno = Turno(primer_jugador)
            self.indice_jugador_actual = self.jugadores.index(self.jugador_actual)
            logging.info(f"Jugadores locales creados: {[j.obtener_nombre() for j in self.jugadores]}, turno inicial: {self.turno.obtener_jugador_actual()}")

            self.turno_actual_cambiado.emit(primer_jugador)

            if primer_jugador == nombre_local:
                self.iniciar_turno()  
            else:
                self.puede_lanzar = False
                self.deshabilitar_lanzamiento.emit()
        else:
            logging.error("No se pudo determinar el jugador local.")

    def resetear_tiradas(self):
        self.tiradas_restantes = 0
        self.dados_actuales = [None] * 5
        self.dados_bloqueados = [False] * 5
        self.actualizar_tiradas_restantes.emit(self.tiradas_restantes)

    def iniciar_turno(self):
        self.tiradas_restantes = 3
        self.dados_bloqueados = [False] * 5
        self.puede_lanzar = True
        self.actualizar_tiradas_restantes.emit(self.tiradas_restantes)
        self.habilitar_lanzamiento.emit()
        logging.info(f"Turno iniciado. Tiradas restantes: {self.tiradas_restantes}")

    def lanzar_dados(self):
        if not self.puede_lanzar or self.tiradas_restantes <= 0:
            logging.warning("No es el turno para lanzar o no quedan tiradas")
            return

        for i in range(5):
            if not self.dados_bloqueados[i]:
                self.dados_actuales[i] = Dado().lanzar()

        self.tiradas_restantes -= 1
        self.actualizar_tiradas_restantes.emit(self.tiradas_restantes)
        logging.info(f"Tirada realizada. Restantes: {self.tiradas_restantes} - Dados: {self.dados_actuales}")

        self.mostrar_resultados_lanzamiento.emit(self.jugador_actual.obtener_nombre(), self.dados_actuales)

        if self.cliente:
            self.cliente.emit('lanzar_dados', {
                'sala_id': self.sala_id_actual,
                'resultados': self.dados_actuales,
                'tiradas_restantes': self.tiradas_restantes
            })

        if self.tiradas_restantes == 0:
            self.puede_lanzar = False
            self.deshabilitar_lanzamiento.emit()

    def pasar_turno(self):
        if self.jugadores:
            self.resetear_tiradas()
            self.indice_jugador_actual = (self.indice_jugador_actual + 1) % len(self.jugadores)
            nuevo_jugador = self.jugadores[self.indice_jugador_actual]
            self.turno.reiniciar_turno(nuevo_jugador.obtener_nombre())

            self.turno_actual_cambiado.emit(self.turno.obtener_jugador_actual())
            logging.info(f"Turno cambiado a: {self.turno.obtener_jugador_actual()}")

            if nuevo_jugador.obtener_nombre() == self.jugador_actual.obtener_nombre():
                self.iniciar_turno()
            else:
                self.puede_lanzar = False
                self.deshabilitar_lanzamiento.emit()

    def recibir_resultados_lanzamiento(self, jugador_sid, resultados, tiradas_restantes=None):
        logging.info(f"Resultados del lanzamiento del jugador {jugador_sid}: {resultados}")

        self.mostrar_resultados_lanzamiento.emit(jugador_sid, resultados)

        jugador_oponente = next((j for j in self.jugadores if j.obtener_nombre() != self.jugador_actual.obtener_nombre()), None)
        if jugador_oponente and jugador_sid != self.jugador_actual.obtener_nombre():
            self.dados_actuales = resultados
            self.actualizar_tiradas_restantes.emit(tiradas_restantes if tiradas_restantes is not None else 0)

    def gestionar_bloqueo_dado(self, indice_dado: int):
        if 0 <= indice_dado < 5 and self.tiradas_restantes < 3:
            self.dados_bloqueados[indice_dado] = not self.dados_bloqueados[indice_dado]
            logging.info(f"Dado {indice_dado} bloqueado: {self.dados_bloqueados[indice_dado]}")




