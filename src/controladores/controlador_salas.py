from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QObject, Signal, Slot
from vista.pantalla_conexion import Ui_ConexionEnRed
import socketio
import time

cliente = socketio.Client()

class ControladorSalas(QObject):
    actualizar_mensajes = Signal(str)
    actualizar_salas = Signal(dict)
    deshabilitar_botones = Signal(bool)

    def __init__(self):
        super().__init__()
        self.ui = None
        self.actualizar_mensajes.connect(self.mostrar_mensaje)
        self.actualizar_salas.connect(self.mostrar_salas)
        self.deshabilitar_botones.connect(self.actualizar_estado_botones)

    @Slot(str)
    def mostrar_mensaje(self, mensaje):
        self.ui.area_mensajes.append(mensaje)

    @Slot(dict)
    def mostrar_salas(self, salas):
        self.ui.area_mensajes.clear()
        if salas:
            self.ui.area_mensajes.append("Salas disponibles:")
            for sala_id, info in salas.items():
                self.ui.area_mensajes.append(f"- {sala_id}: {len(info['jugadores'])} jugadores")
        else:
            self.ui.area_mensajes.append("No hay salas disponibles.")

    @Slot(bool)
    def actualizar_estado_botones(self, deshabilitar):
        self.ui.btn_crear_sala.setDisabled(deshabilitar)
        self.ui.btn_unirse_a_sala.setDisabled(deshabilitar)
        self.ui.btn_listar_salas.setDisabled(deshabilitar)

    def conectar_servidor(self):
        while True:
            try:
                cliente.connect('http://localhost:5000')
                self.actualizar_mensajes.emit("Conectado al servidor.")
                break
            except Exception as e:
                self.actualizar_mensajes.emit(f"Error al conectar: {e}. Intentando reconectar en 5 segundos...")
                time.sleep(5)

    def crear_sala(self):
        nombre = self.ui.entrada_nombre.text().strip()
        if nombre:
            cliente.emit('crear_sala', {'nombre': nombre})
            self.actualizar_mensajes.emit(f"{nombre} está creando una sala...")
            self.deshabilitar_botones.emit(True)
        else:
            self.actualizar_mensajes.emit("Por favor, ingresa tu nombre antes de crear una sala.")

    def unirse_a_sala(self):
        nombre = self.ui.entrada_nombre.text().strip()
        sala_id = self.ui.entrada_id_sala.text().strip()
        if not nombre:
            self.actualizar_mensajes.emit("Por favor, ingresa tu nombre antes de unirte a una sala.")
        elif not sala_id:
            self.actualizar_mensajes.emit("Por favor, ingresa el ID de la sala.")
        else:
            cliente.emit('unirse_a_sala', {'sala_id': sala_id, 'nombre': nombre})
            self.actualizar_mensajes.emit(f"{nombre} está intentando unirse a la sala: {sala_id}")
            self.deshabilitar_botones.emit(True)

    def listar_salas(self):
        cliente.emit('listar_salas')

# Manejadores de eventos del servidor
@cliente.event
def connect():
    print("Conectado al servidor")

@cliente.event
def servidor_conectado(data):
    print(data['mensaje'])

@cliente.event
def sala_creada(data):
    print(f"Sala creada: {data['sala_id']}")
    controlador.actualizar_mensajes.emit(data['mensaje'])  # Mostrar el mensaje "Sala creada. Esperando oponente..."
    controlador.ui.entrada_id_sala.clear()
    controlador.deshabilitar_botones.emit(False)

@cliente.event
def sala_actualizada(data):
    print(f"Sala actualizada: {data}")
    controlador.actualizar_mensajes.emit(data['mensaje'])  # Mostrar el mensaje "El jugador X se ha unido a la sala."
    controlador.deshabilitar_botones.emit(False)

@cliente.event
def partida_iniciada(data):
    print(f"Partida iniciada en la sala: {data['sala_id']}")
    controlador.actualizar_mensajes.emit(f"La partida ha comenzado en la sala {data['sala_id']}.")
    controlador.deshabilitar_botones.emit(True)

@cliente.event
def salas_disponibles(data):
    print("Salas disponibles recibidas:", data)
    controlador.actualizar_salas.emit(data['salas'])

@cliente.event
def error(data):
    print(f"Error: {data['mensaje']}")
    controlador.actualizar_mensajes.emit(f"Error: {data['mensaje']}")
    controlador.deshabilitar_botones.emit(False)

@cliente.event
def jugador_desconectado(data):
    controlador.actualizar_mensajes.emit(f"El jugador {data['jugador']} se ha desconectado de la sala {data['sala_id']}.")

@cliente.event
def disconnect():
    controlador.actualizar_mensajes.emit("Desconectado del servidor. Intentando reconectar...")
    controlador.conectar_servidor()

if __name__ == "__main__":
    app = QApplication([])
    ventana = QMainWindow()
    ui = Ui_ConexionEnRed()
    ui.setupUi(ventana)
    controlador = ControladorSalas()
    controlador.ui = ui
    ui.btn_crear_sala.clicked.connect(controlador.crear_sala)
    ui.btn_unirse_a_sala.clicked.connect(controlador.unirse_a_sala)
    ui.btn_listar_salas.clicked.connect(controlador.listar_salas)
    controlador.conectar_servidor()
    ventana.show()
    app.exec()




