from PySide6.QtCore import QObject, Signal
from typing import List, Optional

from modelo.jugador import Jugador
from modelo.turno import Turno
from modelo.dado import Dado
from modelo.categoria import Categoria
from modelo.puntaje import Puntaje
import logging
import socketio

logging.basicConfig(level=logging.INFO)


class ControladorJuego(QObject):
    turno_actual_cambiado = Signal(str)
    habilitar_lanzamiento = Signal()
    deshabilitar_lanzamiento = Signal()
    mostrar_resultados_lanzamiento = Signal(str, list)
    actualizar_tiradas_restantes = Signal(int)
    habilitar_categorias = Signal()
    deshabilitar_categorias = Signal()

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
        self.tirada_realizada = False
        self.categoria = Categoria()
        self.vista = None
        self.puntaje: Optional[Puntaje] = None

    def set_cliente(self, cliente: socketio.Client):
        self.cliente = cliente

    def set_vista(self, vista):
        self.vista = vista

    def iniciar_partida(self, nombres_jugadores: List[str], nombre_local: str, sala_id: Optional[str] = None,primer_jugador: Optional[str] = None):
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
            self.puntaje = Puntaje([j.obtener_nombre() for j in self.jugadores])
            if self.cliente:
                self.puntaje.set_cliente(self.cliente)
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
        self.tiradas_restantes = 3
        self.dados_actuales = [None] * 5
        self.dados_bloqueados = [False] * 5
        self.actualizar_tiradas_restantes.emit(self.tiradas_restantes)
        if hasattr(self, 'vista') and self.vista.estilo:
            self.vista.estilo.limpiar_tiradas()

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

        if not hasattr(self, 'tirada_realizada'):
            self.tirada_realizada = False

        if not self.tirada_realizada:
            self.tirada_realizada = True
            self.habilitar_categorias.emit()
            logging.info("Primera tirada realizada - Categorías habilitadas")

        self.mostrar_resultados_lanzamiento.emit(self.jugador_actual.obtener_nombre(), self.dados_actuales)

        if self.cliente:
            self.cliente.emit('lanzar_dados', {
                'sala_id': self.sala_id_actual,
                'resultados': self.dados_actuales,
                'tiradas_restantes': self.tiradas_restantes,
                'es_primer_tiro': not self.tirada_realizada
            })

        if self.tiradas_restantes == 0:
            self.puede_lanzar = False
            self.deshabilitar_lanzamiento.emit()
            logging.info("Tiradas agotadas para este turno")

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

    def ha_marcado_categoria(self, categoria: str) -> bool:
        if not hasattr(self, 'vista') or not self.vista or not self.jugador_actual:
            return False

        try:
            return self.vista.ha_marcado_categoria(
                self.jugador_actual.obtener_nombre(),
                categoria
            )
        except (AttributeError, TypeError) as e:
            logging.warning(f"No se pudo verificar categoría: {str(e)}")
            return False

    def pasar_turno(self):
        if not self.jugadores:
            return

        self.resetear_tiradas()
        self.indice_jugador_actual = (self.indice_jugador_actual + 1) % len(self.jugadores)
        nuevo_jugador = self.jugadores[self.indice_jugador_actual]

        self.turno.reiniciar_turno(nuevo_jugador.obtener_nombre())
        self.turno_actual_cambiado.emit(self.turno.obtener_jugador_actual())
        self.tirada_realizada = False

        if nuevo_jugador.obtener_nombre() == self.jugador_actual.obtener_nombre():
            self.iniciar_turno()
        else:
            self.puede_lanzar = False
            self.deshabilitar_lanzamiento.emit()
            self.deshabilitar_categorias.emit()

    def calcular_puntos_para_categoria(self, dados: list, categoria: str) -> int:
        puntos = self.categoria.calcular_puntos(
            dados=[d for d in dados if d is not None],
            categoria=categoria,
            ha_marcado_generala=self.ha_marcado_categoria("Generala")
        )

        try:
            self.puntaje.registrar_puntos(self.jugador_actual.obtener_nombre(),categoria,puntos)

            if self.cliente:
                self.cliente.emit('actualizar_puntajes', {
                    'sala_id': self.sala_id_actual,
                    'puntajes': self.puntaje.obtener_puntajes()
                })

            return puntos

        except ValueError as e:
            logging.error(f"Error al registrar puntos: {str(e)}")
            raise