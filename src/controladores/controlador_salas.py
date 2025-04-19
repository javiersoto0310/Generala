from PySide6.QtCore import QObject, Signal
from src.red.conexion_thread import SocketIOThread
import socketio
import logging

logging.basicConfig(level=logging.INFO)

class ControladorSalas(QObject):
    mostrar_juego = Signal(str, list, str)
    error = Signal(str)
    conexion_exitosa = Signal()
    mostrar_salas = Signal(list)
    iniciar_partida_signal = Signal(list, str)
    nombre_jugador_actual = None

    def __init__(self):
        super().__init__()
        self.ui = None
        self.cliente = socketio.Client(reconnection_attempts=5, reconnection_delay=2000)
        self.socket_thread = SocketIOThread(self.cliente)
        self.controlador_juego = None
        self.setup_handlers()
        self.socket_thread.start()

    def setup_handlers(self):
        @self.cliente.event
        def connect():
            logging.info("Conectado al servidor")
            self.conexion_exitosa.emit()
            if self.ui and self.ui.entrada_nombre.text():
                self.nombre_jugador_actual = self.ui.entrada_nombre.text().strip()

        @self.cliente.event
        def connect_error(data):
            self.error.emit("Error al conectar con el servidor")

        @self.cliente.event
        def disconnect():
            self.error.emit("Desconectado del servidor")

        @self.cliente.event
        def sala_creada(data):
            if 'sala_id' in data:
                logging.info(f"Sala creada: {data['sala_id']}")

        @self.cliente.event
        def lista_salas(data):
            if isinstance(data, list):
                self.mostrar_salas.emit(data)
            else:
                self.error.emit("Error al recibir la lista de salas")

        @self.cliente.event
        def esperar_inicio(data):
            if 'sala_id' in data:
                logging.info(f"Esperando inicio en la sala: {data['sala_id']}")
                self.cliente.emit('cliente_listo', {'sala_id': data['sala_id']})

        @self.cliente.event
        def juego_listo(data):
            if 'sala_id' in data:
                logging.info(f"Juego listo, iniciando en sala: {data['sala_id']}")

        @self.cliente.event
        def sala_unida(data):
            if 'sala_id' in data:
                logging.info(f"Unido a la sala: {data['sala_id']}")

        @self.cliente.event
        def error(data):
            self.error.emit(data.get('mensaje', 'Error desconocido'))

        @self.cliente.event
        def iniciar_juego(data):
            logging.info(f"Evento 'iniciar_juego' recibido para la sala: {data.get('sala_id')}")
            if 'sala_id' in data and 'jugadores' in data and 'primer_jugador' in data:
                sala_id = data['sala_id']
                jugadores = data['jugadores']
                primer_jugador = data['primer_jugador']
                self.mostrar_juego.emit(sala_id, jugadores,primer_jugador)
                logging.warning(f"Evento 'iniciar_juego' recibido con datos incompletos: {data}")

    def crear_sala(self):
        if not self.cliente.connected:
            self.error.emit("No hay conexión con el servidor")
            return

        nombre = self.ui.entrada_nombre.text().strip()
        if not nombre:
            self.error.emit("Debe ingresar un nombre")
            return
        self.nombre_jugador_actual = nombre
        try:
            self.cliente.emit('crear_sala', {'nombre': nombre})
        except Exception as e:
            self.error.emit(f"Error al crear sala: {str(e)}")

    def listar_salas(self):
        if not self.cliente.connected:
            self.error.emit("No hay conexión con el servidor")
            return

        try:
            self.cliente.emit('listar_salas')
        except Exception as e:
            self.error.emit(f"Error al listar salas: {str(e)}")

    def unirse_a_sala(self):
        if not self.cliente.connected:
            self.error.emit("No hay conexión con el servidor")
            return

        nombre = self.ui.entrada_nombre.text().strip()
        sala_id = self.ui.entrada_id_sala.text().strip()

        if not nombre or not sala_id:
            self.error.emit("Debe ingresar nombre y ID de sala")
            return
        self.nombre_jugador_actual = nombre
        try:
            self.cliente.emit('unirse_a_sala', {
                'nombre': nombre,
                'sala_id': sala_id
            })
        except Exception as e:
            self.error.emit(f"Error al unirse a sala: {str(e)}")

