from PySide6.QtCore import QThread, Signal
import logging

logging.basicConfig(level=logging.INFO)

class SocketIOThread(QThread):
    conexion_exitosa = Signal()
    error_conexion = Signal(str)

    def __init__(self, cliente):
        super().__init__()
        self.cliente = cliente

    def run(self):
        try:
            logging.info("Intentando conectar al servidor...")
            self.cliente.connect('http://127.0.0.1:5000', wait_timeout=5)
            logging.info("Conexión exitosa")
            self.conexion_exitosa.emit()
        except Exception as e:
            self.error_conexion.emit(f"Error de conexión: {str(e)}")
