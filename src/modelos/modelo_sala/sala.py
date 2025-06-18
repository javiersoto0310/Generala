import logging
from typing import Optional

from modelos.modelo_juego.jugador import Jugador
from modelos.modelo_juego.puntaje import Puntaje
from modelos.modelo_juego.temporizador import Temporizador

class Sala:
    def __init__(self, sala_id: str, creador_sid: str, jugador: Jugador):
        self.sala_id = sala_id
        self.creador_sid = creador_sid
        self.jugadores: list[Jugador] = [jugador]
        self.sids: list[str] = [creador_sid]
        self.listo: list[str] = []
        self.temporizador = Temporizador(self)
        self.puntaje: Optional[Puntaje] = None
        self.jugador_actual: Optional[str] = None
        self.inacciones: dict[str, int] = {}
        self.temporizador_activo: bool = False
        self.temporizador_id: Optional[str] = None
        self.tarea_temporizador = None

    def agregar_jugador_y_sid(self, sid: str, jugador: Jugador):
        self.sids.append(sid)
        self.jugadores.append(jugador)

    def eliminar_jugador_por_sid(self, sid: str):
        if sid in self.sids:
            index = self.sids.index(sid)
            self.sids.pop(index)
            self.jugadores.pop(index)
            if sid in self.listo:
                self.listo.remove(sid)

    def obtener_oponente_sid(self, sid: str) -> Optional[str]:
        for otro_sid in self.sids:
            if otro_sid != sid:
                return otro_sid
        return None

    def obtener_jugador_por_sid(self, sid: str) -> Optional[Jugador]:
        if sid in self.sids:
            index = self.sids.index(sid)
            return self.jugadores[index]
        return None

    def nombres_de_jugadores(self) -> list[str]:
        return [j.obtener_nombre() for j in self.jugadores]

    def esta_llena(self) -> bool:
        return len(self.jugadores) >= 2

    def esta_vacia(self) -> bool:
        return len(self.jugadores) == 0

    def manejar_tiempo_agotado(self, sio):
        sio.emit('turno_agotado', {'sala_id': self.sala_id}, room=self.sala_id)

        if not self.jugador_actual:
            return

        if self.jugador_actual not in self.inacciones:
            self.inacciones[self.jugador_actual] = 0
        self.inacciones[self.jugador_actual] += 1

        if self.inacciones[self.jugador_actual] >= 3:
            jugadores = self.nombres_de_jugadores()
            oponente = next((j for j in jugadores if j != self.jugador_actual), None)

            if oponente:
                puntajes_totales = {
                    jugador: self.puntaje.obtener_puntaje_total(jugador)
                    for jugador in jugadores
                } if self.puntaje else {}

                mensaje = f"¡{oponente} gana por inactividad de {self.jugador_actual}!\n\n"
                mensaje += "Resultado final:\n"
                for jugador, puntos in puntajes_totales.items():
                    mensaje += f"{jugador}: {puntos} puntos\n"

                sio.emit('juego_finalizado', {
                    'ganador': oponente,
                    'puntajes': puntajes_totales,
                    'motivo': mensaje
                }, room=self.sala_id)
                return

        controlador_puntaje = self.puntaje
        if not controlador_puntaje:
            return

        categorias = controlador_puntaje.obtener_categorias_disponibles(self.jugador_actual)
        if categorias:
            orden_inverso = list(reversed(Puntaje.categorias_ordenadas))
            for categoria in orden_inverso:
                if categoria in categorias:
                    controlador_puntaje.registrar_puntos(self.jugador_actual, categoria, 0)
                    break

            sio.emit('actualizar_puntajes', {
                'sala_id': self.sala_id,
                'puntajes': controlador_puntaje.obtener_puntajes()
            }, room=self.sala_id)

        self.cambiar_turno(sio)

    def cambiar_turno(self, sio):
        try:
            if not self.jugadores:
                logging.warning("No hay jugadores en la sala para cambiar turno")
                return

            jugador_actual = self.obtener_jugador_actual()
            if not jugador_actual:
                logging.error("No se pudo encontrar al jugador actual")
                return

            siguiente_jugador = self.obtener_siguiente_jugador(jugador_actual)
            if not siguiente_jugador:
                logging.error("No se pudo determinar siguiente jugador")
                return

            self.jugador_actual = siguiente_jugador.obtener_nombre()

            self.notificar_cambio_turno(sio, siguiente_jugador)
            sio.emit('limpiar_interfaz', {'sala_id': self.sala_id}, room=self.sala_id)

            self.temporizador.iniciar(sio)

        except Exception as error:
            logging.error(f"Error al cambiar turno: {str(error)}", exc_info=True)
            raise

    def obtener_jugador_actual(self) -> Optional[Jugador]:
        if not self.jugador_actual:
            return None
        return next((jugador for jugador in self.jugadores if jugador.obtener_nombre() == self.jugador_actual), None)

    def obtener_siguiente_jugador(self, jugador_actual: Jugador) -> Optional[Jugador]:
        try:
            indice_actual = self.jugadores.index(jugador_actual)
            indice_siguiente = (indice_actual + 1) % len(self.jugadores)
            return self.jugadores[indice_siguiente]
        except ValueError:
            return None

    def notificar_cambio_turno(self, sio, siguiente_jugador: Jugador):
        siguiente_sid = self.sids[self.jugadores.index(siguiente_jugador)]
        sio.emit('cambio_de_turno', {
            'sala_id': self.sala_id,
            'jugador_actual': siguiente_sid,
            'jugador_actual_nombre': siguiente_jugador.obtener_nombre(),
            'es_tu_turno': True
        }, room=self.sala_id)
