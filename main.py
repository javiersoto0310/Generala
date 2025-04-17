import logging
import sys
from typing import Optional, List

from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtCore import QObject, Qt

from vista.pantalla_conexion import Conexion
from vista.pantalla_juego import PantallaJuego
from controladores.controlador_salas import ControladorSalas
from controladores.controlador_juego import ControladorJuego


class MainApp(QObject):
    controlador_salas: ControladorSalas
    controlador_juego: ControladorJuego
    ventana_conexion: QMainWindow
    ventana_juego: QMainWindow

    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)

        self.ventana_conexion = QMainWindow()
        self.ui_conexion = Conexion()
        self.ui_conexion.setupUi(self.ventana_conexion)

        self.ventana_juego = QMainWindow()
        self.ui_juego = PantallaJuego()
        self.ui_juego.setupUi(self.ventana_juego)

        self.controlador_juego = ControladorJuego()
        self.controlador_salas = ControladorSalas()
        self.controlador_salas.ui = self.ui_conexion
        self.controlador_salas.controlador_juego = self.controlador_juego
        self.ui_conexion.btn_crear_sala.clicked.connect(self.crear_sala)
        self.ui_conexion.btn_unirse_a_sala.clicked.connect(self.unirse_a_sala)
        self.ui_conexion.btn_listar_salas.clicked.connect(self.controlador_salas.listar_salas)

        self.controlador_salas.mostrar_juego.connect(self.mostrar_ventana_juego, Qt.QueuedConnection)
        self.controlador_salas.error.connect(self.mostrar_error, Qt.QueuedConnection)
        self.controlador_salas.conexion_exitosa.connect(self.on_conexion_exitosa, Qt.QueuedConnection)
        self.controlador_salas.mostrar_salas.connect(self.mostrar_salas)

        self.ventana_conexion.show()
        sys.exit(self.app.exec())

    def on_conexion_exitosa(self):
        self.ui_conexion.area_mensajes.append("Conectado al servidor")

    def crear_sala(self):
        if not self.controlador_salas.cliente.connected:
            QMessageBox.critical(
                self.ventana_conexion,
                "Error",
                "Espere a establecer conexión con el servidor"
            )
            return
        self.controlador_salas.crear_sala()

    def unirse_a_sala(self):
        if not self.controlador_salas.cliente.connected:
            QMessageBox.critical(
                self.ventana_conexion,
                "Error",
                "Espere a establecer conexión con el servidor"
            )
            return
        self.controlador_salas.unirse_a_sala()

    def mostrar_salas(self, lista_salas: List[dict]):
        mensaje = "Salas disponibles:\n"
        for sala in lista_salas:
            mensaje += f"- {sala['sala_id']}: {', '.join(sala['jugadores'])}\n"
        self.ui_conexion.area_mensajes.setPlainText(mensaje)

    def mostrar_ventana_juego(self, sala_id: str, jugadores: List[str]):
        logging.info(f"Mostrando pantalla de juego para la sala: {sala_id} con jugadores: {jugadores}")
        self.ventana_conexion.hide()
        self.ventana_juego.setWindowTitle(f"Generala - Sala: {sala_id}")
        self.ventana_juego.show()
        if self.controlador_juego:
            self.controlador_juego.iniciar_partida(jugadores, self.controlador_salas.nombre_jugador_actual)

    def mostrar_error(self, mensaje: str):
        QMessageBox.warning(self.ventana_conexion, "Error", mensaje)


if __name__ == "__main__":
    app = MainApp()