from PySide6.QtWidgets import QMainWindow, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal
from vista.pantalla_juego import PantallaJuego
from vista.estilo_pantalla_juego import Estilo
import logging

logging.basicConfig(level=logging.INFO)


class JuegoVentana(QMainWindow, PantallaJuego):
    def __init__(self):
        super().__init__()
        super().setupUi(self)

        self.label_jugador_actual = self.findChild(QLabel, 'jugador_actual')
        self.lanzar_dados_btn = self.findChild(QPushButton, 'lanzar_dados')

        if not self.label_jugador_actual:
            logging.error("Error crítico: QLabel 'jugador_actual' no encontrado")
        else:
            self.label_jugador_actual.setText("Turno de: -")

        if self.lanzar_dados_btn:
            self.lanzar_dados_btn.setEnabled(False)

        self.estilo = Estilo(self)
        logging.info("Ventana de juego inicializada correctamente")

    def habilitar_boton_lanzar(self):
        if self.lanzar_dados_btn:
            self.lanzar_dados_btn.setEnabled(True)
            logging.info("Botón lanzar HABILITADO")

    def deshabilitar_boton_lanzar(self):
        if self.lanzar_dados_btn:
            self.lanzar_dados_btn.setEnabled(False)
            logging.info("Botón lanzar DESHABILITADO")

    def actualizar_jugador_actual(self, nombre_jugador: str):
        if hasattr(self, 'label_jugador_actual') and self.label_jugador_actual:
            self.label_jugador_actual.setText(f"Turno de: {nombre_jugador}")
            logging.info(f"Actualizado jugador actual: {nombre_jugador}")
        else:
            logging.error("No se pudo actualizar jugador actual: label no disponible")

    def actualizar_dados_lanzados(self, jugador_sid, resultados):
        self.estilo.mostrar_dados(resultados)
