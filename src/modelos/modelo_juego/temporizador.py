from eventlet import sleep
from uuid import uuid4
import logging

class Temporizador:
    def __init__(self, sala, tiempo_inicial=30):
        self.sala = sala
        self.__tiempo_turno = tiempo_inicial
        self.__segundos_restantes = tiempo_inicial
        self._temporizador_en_marcha = False
        self._proceso_temporizador = None
        self.__id_temporizador = None

    def obtener_tiempo_restante(self):
        return self.__segundos_restantes

    def obtener_tiempo_turno(self):
        return self.__tiempo_turno

    def obtener_id_temporizador(self):
        return self.__id_temporizador

    def iniciar(self, sio):
        self.detener()
        self.__segundos_restantes = self.__tiempo_turno
        self._temporizador_en_marcha = True
        self.__id_temporizador = uuid4().hex

        def cuenta_regresiva(id_temp):
            try:
                while (self.__segundos_restantes > 0 and
                       self._temporizador_en_marcha and self.__id_temporizador == id_temp):
                    sleep(1)
                    self.__segundos_restantes -= 1
                    sio.emit('cronometro_actualizado', {
                        'sala_id': self.sala.sala_id,
                        'tiempo_restante': self.__segundos_restantes
                    }, room=self.sala.sala_id)

                if self._temporizador_en_marcha and self.__id_temporizador == id_temp:
                    self.sala.manejar_tiempo_agotado(sio)

            except Exception as e:
                logging.error(f"[Temporizador] Error en cuenta_regresiva: {e}")
                self.detener()

        self._proceso_temporizador = sio.start_background_task(cuenta_regresiva, self.__id_temporizador)

    def detener(self):
        self._temporizador_en_marcha = False
        self._proceso_temporizador = None
        self.__id_temporizador = None
