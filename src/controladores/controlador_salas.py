from PySide6.QtCore import QObject, Signal
from red.conexion_inicial import SocketIOThread
import socketio
import logging

logging.basicConfig(level=logging.INFO)

class ControladorSalas(QObject):
    mostrar_juego = Signal(str, list, str)
    error = Signal(str)
    conexion_exitosa = Signal(dict)
    mostrar_salas = Signal(list)
    nombre_jugador_actual = None
    mostrar_mensaje = Signal(str)

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
            datos_conexion = {
                'sid': self.cliente.sid,
                'nombre_jugador': self.ui.entrada_nombre.text().strip() if self.ui else None
            }
            self.conexion_exitosa.emit(datos_conexion)

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

        @self.cliente.event
        def ya_tiene_sala(data):
            if 'mensaje' in data:
                self.mostrar_mensaje.emit(data['mensaje'])

        @self.cliente.event
        def sala_cerrada_inactividad(data):
            if 'mensaje' in data:
                self.mostrar_mensaje.emit(data['mensaje'])

        @self.cliente.event
        def esperar_inicio(data):
            if 'sala_id' in data:
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
            if 'sala_id' in data and 'jugadores' in data and 'primer_jugador' in data:
                self.mostrar_juego.emit(data['sala_id'], data['jugadores'], data['primer_jugador'])

        @self.cliente.event
        def resultados_lanzamiento(data):
            if 'resultados' in data and self.controlador_juego:
                self.controlador_juego.recibir_resultados_lanzamiento(
                    data['jugador_sid'],
                    data['resultados'],
                    data.get('tiradas_restantes')
                )

    def crear_sala(self, nombre: str):
        if not self.cliente.connected:
            self.error.emit("No hay conexión con el servidor")
            return

        nombre = nombre.strip()
        if not nombre:
            self.error.emit("Debe ingresar un nombre válido")
            return

        if len(nombre) > 15:
            self.error.emit("Nombre muy largo (máx. 15 caracteres)")
            return

        try:
            self.nombre_jugador_actual = nombre
            self.cliente.emit('crear_sala', {'nombre': nombre})
            self.mostrar_mensaje.emit("Sala creada. Esperando oponente...")
        except Exception as e:
            self.error.emit(f"Error al crear sala: {str(e)}")

    def listar_salas(self, nombre: str = None):
        if not self.cliente.connected:
            self.error.emit("Error: No hay conexión con el servidor")
            return

        if nombre is not None and not nombre.strip():
            self.error.emit("Error: Debe ingresar un nombre válido")
            return

        try:
            self.cliente.emit('listar_salas')
            if nombre is not None:
                self.mostrar_mensaje.emit("Buscando salas disponibles...")
        except Exception as e:
            self.error.emit(f"Error al listar salas: {str(e)}")

    def unirse_a_sala(self, sala_id: str, nombre: str):
        if not self.cliente.connected:
            self.error.emit("No hay conexión con el servidor")
            return

        nombre = nombre.strip()
        if not nombre:
            self.error.emit("Debe ingresar un nombre válido")
            return

        if not sala_id:
            self.error.emit("Sala no válida")
            return

        try:
            self.nombre_jugador_actual = nombre
            self.cliente.emit('unirse_a_sala', {
                'nombre': nombre,
                'sala_id': sala_id
            })
            self.mostrar_mensaje.emit(f"Uniéndose a sala {sala_id}...")
        except Exception as e:
            self.error.emit(f"Error al unirse a sala: {str(e)}")
