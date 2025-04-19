from PySide6.QtWidgets import QMainWindow, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal
from vista.pantalla_juego import PantallaJuego
from vista.estilo_pantalla_juego import Estilo
import logging

logging.basicConfig(level=logging.INFO)


class JuegoVentana(QMainWindow, PantallaJuego):
    def __init__(self, controlador=None):
        super().__init__()
        super().setupUi(self)

        self.controlador = controlador
        self.label_jugador_actual = self.findChild(QLabel, 'jugador_actual')
        self.lanzar_dados_btn = self.findChild(QPushButton, 'lanzar_dados')
        self.contador_tiradas_label = self.findChild(QLabel, 'contador_tiradas')

        if not self.label_jugador_actual:
            logging.error("Error crítico: QLabel 'jugador_actual' no encontrado")
        else:
            self.label_jugador_actual.setText("Turno de: -")

        if self.lanzar_dados_btn:
            self.lanzar_dados_btn.setEnabled(False)

        if self.contador_tiradas_label:
            self.contador_tiradas_label.setText("Tiradas: 0")

        self.estilo = Estilo(self)

        self.configurar_clicks_dados()
        logging.info("Ventana de juego inicializada correctamente")

        if controlador:
            controlador.mostrar_resultados_lanzamiento.connect(self.actualizar_dados_lanzados)

    def configurar_clicks_dados(self):
        for i, dado_label in enumerate(self.estilo.dados_labels):
            if dado_label:
                dado_label.mousePressEvent = lambda event, idx=i: self.toggle_dado_bloqueado(idx)

    def toggle_dado_bloqueado(self, indice_dado):
        if self.controlador and hasattr(self.controlador, 'tiradas_restantes'):
            if self.controlador.tiradas_restantes < 3:  # Solo después de la primera tirada
                self.controlador.dados_bloqueados[indice_dado] = not self.controlador.dados_bloqueados[indice_dado]
                self.estilo.aplicar_estilo_seleccionado(indice_dado, self.controlador.dados_bloqueados[indice_dado])
                logging.info(f"Dado {indice_dado} bloqueado: {self.controlador.dados_bloqueados[indice_dado]}")

    def actualizar_contador_tiradas(self, tiradas_restantes):
        if hasattr(self, 'contador_tiradas_label') and self.contador_tiradas_label:
            self.contador_tiradas_label.setText(f"Tiradas: {tiradas_restantes}")
            logging.info(f"Actualizado contador de tiradas: {tiradas_restantes}")

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
        if not resultados:
            return

        self.estilo.mostrar_dados(resultados)

        if hasattr(self.controlador, 'tiradas_restantes'):
            self.estilo.actualizar_imagen_tirada(self.controlador.tiradas_restantes)

        if (hasattr(self.controlador, 'jugador_actual') and
                hasattr(self.controlador, 'nombre_jugador_actual') and
                jugador_sid != self.controlador.jugador_actual.obtener_nombre()):
            self.label_jugador_actual.setText(f"Turno de: {jugador_sid} (Oponente)")
            self.deshabilitar_boton_lanzar()

        logging.info(f"Dados actualizados para jugador {jugador_sid}: {resultados}")
