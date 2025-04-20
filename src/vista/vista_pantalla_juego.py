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

        print(f"Estado inicial de tirada1 - Visible: {self.tirada1.isVisible()}, Geometry: {self.tirada1.geometry()}")

        for tirada in [self.tirada1, self.tirada2, self.tirada3]:
            tirada.setVisible(False)
            tirada.raise_()
            tirada.setStyleSheet("background: transparent; border: none;")

        self.controlador = controlador
        self.label_jugador_actual = self.findChild(QLabel, 'jugador_actual')
        self.lanzar_dados_btn = self.findChild(QPushButton, 'lanzar_dados')
        self.Tiradas_agotadas_label = self.findChild(QLabel, 'Tiradas_agotadas')

        if not self.label_jugador_actual:
            logging.error("Error crítico: QLabel 'jugador_actual' no encontrado")
        else:
            self.label_jugador_actual.setText("Turno de: -")

        if self.lanzar_dados_btn:
            self.lanzar_dados_btn.setEnabled(False)

        if self.Tiradas_agotadas_label:
            self.Tiradas_agotadas_label.setText("")

        self.estilo = Estilo(self)

        print(f"Tamaño de tirada1: {self.tirada1.size()}")
        print(f"¿tirada1 es visible? {self.tirada1.isVisible()}")

        self.configurar_clicks_dados()
        logging.info("Ventana de juego inicializada correctamente")

        if controlador:
            controlador.mostrar_resultados_lanzamiento.connect(self.actualizar_dados_lanzados)
            controlador.actualizar_tiradas_restantes.connect(self.estilo.actualizar_imagen_tirada)
            controlador.actualizar_tiradas_restantes.connect(self.actualizar_mensaje_tiradas_agotadas)

    def actualizar_mensaje_tiradas_agotadas(self, tiradas_restantes):
        if self.controlador and hasattr(self.controlador, 'turno') and hasattr(self.controlador.turno, 'obtener_jugador_actual') and hasattr(self.controlador, 'jugador_actual'):
            jugador_activo = self.controlador.turno.obtener_jugador_actual()
            jugador_local = self.controlador.jugador_actual.obtener_nombre()
            if self.Tiradas_agotadas_label:
                if tiradas_restantes == 0 and jugador_activo == jugador_local:
                    self.Tiradas_agotadas_label.setText("Debes seleccionar una categoría!!!")
                else:
                    self.Tiradas_agotadas_label.setText("")
        elif self.Tiradas_agotadas_label:
            self.Tiradas_agotadas_label.setText("")

    def configurar_clicks_dados(self):
        for i, dado_label in enumerate(self.estilo.dados_labels):
            if dado_label:
                dado_label.mousePressEvent = lambda event, idx=i: self.seleccionar_dado_para_bloqueo(idx)

    def seleccionar_dado_para_bloqueo(self, indice_dado):
        if self.controlador and hasattr(self.controlador, 'tiradas_restantes'):
            if self.controlador.tiradas_restantes < 3:
                self.controlador.dados_bloqueados[indice_dado] = not self.controlador.dados_bloqueados[indice_dado]
                self.estilo.aplicar_estilo_seleccionado(indice_dado, self.controlador.dados_bloqueados[indice_dado])
                logging.info(f"Dado {indice_dado} bloqueado: {self.controlador.dados_bloqueados[indice_dado]}")

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