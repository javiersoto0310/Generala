from typing import Optional

from modelo.jugador import Jugador
from modelo.puntaje import Puntaje
from modelo.temporizador import Temporizador

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

    def agregar_jugador(self, sid: str, jugador: Jugador):
        self.sids.append(sid)
        self.jugadores.append(jugador)

    def eliminar_jugador(self, sid: str):
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

            if self.jugador_actual not in self.inacciones:
                self.inacciones[self.jugador_actual] = 0
            self.inacciones[self.jugador_actual] += 1

            if self.inacciones[self.jugador_actual] >= 3:
                jugadores = self.nombres_de_jugadores()
                oponente = next((j for j in jugadores if j != self.jugador_actual), None)
                puntajes_totales = {
                    jugador: controlador_puntaje.obtener_puntaje_total(jugador)
                    for jugador in jugadores
                }
                sio.emit('juego_finalizado', {
                    'ganador': oponente,
                    'puntajes': puntajes_totales,
                    'motivo': f"La partida fue finalizada por inactividad de {self.jugador_actual}."
                }, room=self.sala_id)
                return

        self.cambiar_turno(sio)

    def cambiar_turno(self, sio):
        try:
            if not self.sids or not self.jugadores:
                return

            actual_sid = self.sids[self.jugadores.index(next(j for j in self.jugadores if j.obtener_nombre() == self.jugador_actual))]
            indice_actual = self.sids.index(actual_sid)
            indice_siguiente = (indice_actual + 1) % len(self.sids)
            siguiente_sid = self.sids[indice_siguiente]
            siguiente_nombre = self.jugadores[indice_siguiente].obtener_nombre()

            self.jugador_actual = siguiente_nombre

            sio.emit('cambio_de_turno', {
                'sala_id': self.sala_id,
                'jugador_actual': siguiente_sid,
                'jugador_actual_nombre': siguiente_nombre,
                'es_tu_turno': False
            }, room=self.sala_id)

            sio.emit('limpiar_interfaz', {'sala_id': self.sala_id}, room=self.sala_id)

            self.temporizador.iniciar(sio)

        except Exception as e:
            import logging
            logging.error(f"[Sala] Error en cambiar_turno: {e}")

