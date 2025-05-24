from PySide6.QtCore import QObject, Signal
from typing import List, Optional
from modelo.jugador import Jugador
from modelo.turno import Turno
from modelo.dado import Dado
from modelo.categoria import Categoria
import socketio
import logging

logging.basicConfig(level=logging.INFO)

class ControladorJuego(QObject):
    habilitar_lanzamiento = Signal()
    deshabilitar_lanzamiento = Signal()
    mostrar_resultados_lanzamiento = Signal(str, list)
    actualizar_tiradas_restantes = Signal(int)
    habilitar_categorias = Signal()
    deshabilitar_categorias = Signal()
    cambio_turno_signal = Signal(object)
    jugador_desconectado = Signal(str)
    actualizar_tiempo_restante = Signal(str)  # nueva señal

    def __init__(self):
        super().__init__()
        self.turno: Optional[Turno] = None
        self.jugadores: List[Jugador] = []
        self.jugador_actual: Optional[Jugador] = None
        self.indice_jugador_actual: int = 0
        self.sala_id_actual: Optional[str] = None
        self.cliente: Optional[socketio.Client] = None
        self.tiradas_restantes: int = 0
        self.dados_actuales: List[Optional[int]] = [None] * 5
        self.dados_bloqueados: List[bool] = [False] * 5
        self.tirada_realizada = False
        self.categoria = Categoria()
        self.vista = None
        self.jugador_sid_local: Optional[str] = None

    def set_cliente(self, cliente: socketio.Client):
        self.cliente = cliente
        self._setup_handlers()

    def set_vista(self, vista):
        self.vista = vista
        self.actualizar_tiempo_restante.connect(self.vista.actualizar_tiempo_restante)

    def set_jugador_sid_local(self, sid: str):
        self.jugador_sid_local = sid

    def _setup_handlers(self):
        @self.cliente.on('jugador_desconectado')
        def on_jugador_desconectado(data):
            mensaje = data.get("mensaje", "Fin del juego: un jugador ha abandonado la partida.")
            self.jugador_desconectado.emit(mensaje)

        @self.cliente.event
        def cambio_de_turno(data):
            try:
                if not isinstance(data, dict):
                    return

                jugador_actual_sid = data.get('jugador_actual')
                jugador_actual_nombre = data.get('jugador_actual_nombre')
                sala_id = data.get('sala_id')

                if not all([jugador_actual_sid, jugador_actual_nombre, sala_id]) or sala_id != self.sala_id_actual:
                    return

                if jugador_actual_nombre != self.jugador_actual.obtener_nombre():
                    return

                es_mi_turno = (jugador_actual_sid == self.jugador_sid_local)
                if not es_mi_turno:
                    self.jugador_sid_local = jugador_actual_sid
                    es_mi_turno = True

                if jugador_actual_nombre:
                    self._reiniciar_turno(jugador_actual_nombre, es_mi_turno)
                    self.cambio_turno_signal.emit({
                        'jugador_nombre': jugador_actual_nombre,
                        'es_mi_turno': es_mi_turno,
                        'es_inicio': False
                    })
                else:
                    self.deshabilitar_lanzamiento.emit()

                self.cambio_turno_signal.emit({
                    'jugador_nombre': jugador_actual_nombre,
                    'es_mi_turno': es_mi_turno,
                    'es_inicio': False
                })

            except (TypeError, AttributeError) as error:
                logging.error(f"Error en cambio_de_turno: {error}")
                self.deshabilitar_lanzamiento.emit()
            except Exception as error:
                logging.error(f"Error inesperado en cambio_de_turno: {error}")
                self.deshabilitar_lanzamiento.emit()

        @self.cliente.on('limpiar_interfaz')
        def on_limpiar_interfaz_de_dados_lanzados(data):
            if data.get('sala_id') == self.sala_id_actual:
                self._resetear_estado_turno()
                if self.vista:
                    self.vista.limpiar_interfaz_turno()

        @self.cliente.on('actualizar_puntajes')
        def on_actualizar_puntajes(data):
            logging.info(f"Recibido actualizar_puntajes: {data}")
            if not isinstance(data, dict):
                return

            puntajes = data.get('puntajes')

            if self.vista:
                self.vista.actualizar_tabla_puntajes(puntajes)

        @self.cliente.on('resultados_lanzamiento')
        def on_resultados_lanzamiento(data):
            jugador_sid = data.get("jugador_sid")
            resultados = data.get("resultados")
            tiradas = data.get("tiradas_restantes")
            disponibles = data.get("categorias_disponibles", [])
            self.recibir_resultados_lanzamiento(jugador_sid, resultados, tiradas, disponibles)

        @self.cliente.on('juego_finalizado')
        def on_juego_finalizado(data):
            ganador = data.get('ganador')
            puntajes = data.get('puntajes')
            if self.vista:
                self.vista.mostrar_ganador(ganador, puntajes)
            self.deshabilitar_lanzamiento.emit()

        @self.cliente.on('cronometro_actualizado')
        def on_cronometro_actualizado(data):
            if not isinstance(data, dict):
                return
            tiempo_restante = data.get('tiempo_restante')
            if tiempo_restante is not None:
                self.actualizar_tiempo_restante.emit(f"Tiempo: {tiempo_restante}s")

        @self.cliente.on('turno_agotado')
        def on_turno_agotado(data):
            if data.get('sala_id') == self.sala_id_actual:
                self.pasar_turno()

    def _reiniciar_turno(self, jugador: str, es_mi_turno: bool):
        self.turno.reiniciar_turno(jugador)
        self.indice_jugador_actual = next(
            (i for i, j in enumerate(self.jugadores)
             if j.obtener_nombre() == jugador), 0)

        if es_mi_turno:
            self.iniciar_turno()
            self.habilitar_lanzamiento.emit()
        else:
            self.deshabilitar_lanzamiento.emit()

    def _resetear_estado_turno(self):
        self.resetear_tiradas()
        self.tirada_realizada = False
        self.dados_bloqueados = [False] * 5

    def iniciar_partida(self, nombres_jugadores: List[str], nombre_local: str, sala_id: Optional[str] = None, primer_jugador: Optional[str] = None):
        self.jugadores = [Jugador(nombre) for nombre in nombres_jugadores]
        self.jugador_actual = next(j for j in self.jugadores if j.obtener_nombre() == nombre_local)
        self.sala_id_actual = sala_id

        self.turno = Turno(primer_jugador)

        self.cambio_turno_signal.emit({
            'jugador_nombre': primer_jugador,
            'es_mi_turno': (primer_jugador == nombre_local),
            'es_inicio': True
        })

        if primer_jugador == nombre_local:
            self.iniciar_turno()
        else:
            self.deshabilitar_lanzamiento.emit()

    def resetear_tiradas(self):
        self.tiradas_restantes = 3
        self.dados_actuales = [None] * 5
        self.actualizar_tiradas_restantes.emit(self.tiradas_restantes)

    def iniciar_turno(self):
        self._resetear_estado_turno()
        self.actualizar_tiradas_restantes.emit(self.tiradas_restantes)
        self.habilitar_lanzamiento.emit()

    def lanzar_dados(self):
        if self.tiradas_restantes <= 0:
            return

        for i in range(5):
            if not self.dados_bloqueados[i]:
                self.dados_actuales[i] = Dado().lanzar()

        self.tiradas_restantes -= 1
        self.actualizar_tiradas_restantes.emit(self.tiradas_restantes)

        if not self.tirada_realizada:
            self.tirada_realizada = True
            if self.vista and self.jugador_actual:
                disponibles = self.obtener_categorias_disponibles()
                self.vista.habilitar_categorias_disponibles(disponibles)

        self.mostrar_resultados_lanzamiento.emit(
            self.jugador_actual.obtener_nombre(),
            self.dados_actuales
        )

        if self.cliente:
            disponibles = self.obtener_categorias_disponibles()
            self.cliente.emit('lanzar_dados', {
                'sala_id': self.sala_id_actual,
                'resultados': self.dados_actuales,
                'tiradas_restantes': self.tiradas_restantes,
                'categorias_disponibles': disponibles,
                'es_primer_tiro': not self.tirada_realizada
            })

        if self.tiradas_restantes == 0:
            self.deshabilitar_lanzamiento.emit()

    def obtener_categorias_disponibles(self):
        if not hasattr(self, 'jugador_actual') or not self.jugador_actual:
            return []

        jugador_nombre = self.jugador_actual.obtener_nombre()

        if hasattr(self, 'vista') and self.vista:
            categorias = [
                "1", "2", "3", "4", "5", "6",
                "Escalera", "Full", "Póker", "Generala", "Doble Generala"
            ]
            return [cat for cat in categorias if not self.vista.ha_marcado_categoria(jugador_nombre, cat)]

        return []

    def recibir_resultados_lanzamiento(self, jugador_sid, resultados, tiradas_restantes=None, categorias_disponibles=None):
        self.mostrar_resultados_lanzamiento.emit(jugador_sid, resultados)

        self.dados_actuales = resultados
        self.actualizar_tiradas_restantes.emit(tiradas_restantes or 0)

        if categorias_disponibles and self.vista:
            self.vista.habilitar_categorias_disponibles(categorias_disponibles)

    def _ha_marcado_categoria(self, categoria: str) -> bool:
        if not hasattr(self, 'vista') or not self.vista:
            return False
        return self.vista.ha_marcado_categoria(
            self.jugador_actual.obtener_nombre(),
            categoria
        )

    def pasar_turno(self):
        if not self.jugadores:
            return

        self.deshabilitar_lanzamiento.emit()
        self.deshabilitar_categorias.emit()

        nuevo_indice = (self.indice_jugador_actual + 1) % len(self.jugadores)
        nuevo_jugador = self.jugadores[nuevo_indice]
        nombre_nuevo_jugador = nuevo_jugador.obtener_nombre()

        self._resetear_estado_turno()
        self.indice_jugador_actual = nuevo_indice
        self.turno.reiniciar_turno(nombre_nuevo_jugador)
        self.cambio_turno_signal.emit({
            'jugador_nombre': nombre_nuevo_jugador,
            'es_mi_turno': (nombre_nuevo_jugador == self.jugador_actual.obtener_nombre()),
            'es_inicio': False,
            'tiradas_restantes': self.tiradas_restantes
        })

    def calcular_puntos_para_categoria(self, dados: list, categoria: str) -> int:
        puntos = self.categoria.calcular_puntos(
            dados=[d for d in dados if d is not None],
            categoria=categoria,
            ha_marcado_generala=self._ha_marcado_categoria("Generala")
        )

        if self.cliente:
            self.cliente.emit('actualizar_puntajes', {
                'sala_id': self.sala_id_actual,
                'puntaje_jugador': {
                    self.jugador_actual.obtener_nombre(): {
                        categoria: puntos
                    }
                }
            })

        self.verificar_fin_de_juego()
        return puntos

    def verificar_fin_de_juego(self):
        if self.cliente:
            self.cliente.emit('verificar_fin_juego', {
                'sala_id': self.sala_id_actual
            })

    def turno_agotado(self):
        if not self.jugador_actual:
            return

        jugador_nombre = self.jugador_actual.obtener_nombre()
        disponibles = self.obtener_categorias_disponibles()

        if disponibles:
            categoria_auto = disponibles[0]
            if self.cliente:
                self.cliente.emit('actualizar_puntajes', {
                    'sala_id': self.sala_id_actual,
                    'puntaje_jugador': {
                        jugador_nombre: {
                            categoria_auto: 0
                        }
                    }
                })

        self.verificar_fin_de_juego()
        self.pasar_turno()
