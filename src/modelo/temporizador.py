from eventlet import sleep
from uuid import uuid4
import logging


class Temporizador:
    def __init__(self, sala, tiempo_turno=30):
        self.sala = sala
        self.tiempo_turno = tiempo_turno
        self.segundos_restantes = tiempo_turno
        self.activo = False
        self.tarea = None
        self.id = None

    def iniciar(self, sio):
        self.detener()
        self.segundos_restantes = self.tiempo_turno
        self.activo = True
        self.id = uuid4().hex

        def cuenta_regresiva(id_temp):
            try:
                while (self.segundos_restantes > 0 and
                       self.activo and
                       self.id == id_temp):
                    sleep(1)
                    self.segundos_restantes -= 1
                    sio.emit('cronometro_actualizado', {
                        'sala_id': self.sala.sala_id,
                        'tiempo_restante': self.segundos_restantes
                    }, room=self.sala.sala_id)

                if self.activo and self.id == id_temp:
                    self.sala.manejar_tiempo_agotado(sio)

            except Exception as e:
                logging.error(f"[Temporizador] Error en cuenta_regresiva: {e}")
                self.detener()

        self.tarea = sio.start_background_task(cuenta_regresiva, self.id)

    def detener(self):
        self.activo = False
        self.tarea = None
        self.id = None
