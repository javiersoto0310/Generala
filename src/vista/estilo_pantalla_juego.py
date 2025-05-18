import logging
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class Estilo:
    def __init__(self, ventana_juego):
        self.ventana_juego = ventana_juego
        self.dados_labels = [
            self.ventana_juego.dado1,
            self.ventana_juego.dado2,
            self.ventana_juego.dado3,
            self.ventana_juego.dado4,
            self.ventana_juego.dado5,
        ]
        self.configurar_tamano_dados()
        self.configurar_tamano_tiradas()
        self.dado_imagenes = self.cargar_rutas_imagenes()

    def configurar_tamano_dados(self):
        for lbl in self.dados_labels:
            if lbl:
                lbl.setMinimumSize(50, 50)
                lbl.setMaximumSize(80, 80)

    def configurar_tamano_tiradas(self):
        tirada_labels = [self.ventana_juego.tirada1, self.ventana_juego.tirada2, self.ventana_juego.tirada3]
        for label in tirada_labels:
            if label:
                label.setMinimumSize(50, 50)
                label.setMaximumSize(50, 50)
                label.setScaledContents(True)

    def cargar_rutas_imagenes(self):
        base_path = "recursos/img/"
        return [f"{base_path}dado{i}.png" for i in range(1, 7)]

    def mostrar_dados(self, dados):
        for i in range(5):
            if i < len(self.dados_labels) and self.dados_labels[i]:
                valor = dados[i] if i < len(dados) else None
                if valor is not None and 1 <= valor <= 6:
                    try:
                        pixmap = QPixmap(f"recursos/img/dado{valor}.png")
                        self.dados_labels[i].setPixmap(pixmap.scaled(
                            self.dados_labels[i].size(),
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                        ))
                    except Exception as e:
                        logging.error(f"Error al cargar imagen para dado {valor}: {str(e)}")
                        self.dados_labels[i].setText(str(valor))
                else:
                    self.dados_labels[i].clear()

    def actualizar_imagen_tirada(self, tiradas_restantes):
        try:
            tiradas_realizadas = 3 - tiradas_restantes

            for i, label in enumerate([self.ventana_juego.tirada1,
                                     self.ventana_juego.tirada2,
                                     self.ventana_juego.tirada3], start=1):
                if not label:
                    continue

                if i <= tiradas_realizadas:
                    img_path = f"recursos/img/tirada{i}.png"
                    pixmap = QPixmap(img_path)

                    if not pixmap.isNull():
                        label.setPixmap(pixmap.scaled(
                            label.size(),
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                        ))
                        label.show()
                else:
                    label.clear()
        except Exception as e:
            logging.error(f"Error en actualizar_imagen_tirada: {str(e)}")

    def aplicar_estilo_seleccionado(self, indice_dado, seleccionado):
        estilo = "border: 2px solid #A0A0A0;" if seleccionado else "border: none;"
        if indice_dado < len(self.dados_labels) and self.dados_labels[indice_dado]:
            self.dados_labels[indice_dado].setStyleSheet(estilo)

    def limpiar_dados(self):
        for lbl in self.dados_labels:
            if lbl:
                lbl.clear()
                lbl.setStyleSheet("")

    def resetear_estilos_dados(self):
        for lbl in self.dados_labels:
            if lbl:
                lbl.setStyleSheet("")
                lbl.setProperty("bloqueado", False)

    def limpiar_tiradas(self):
        if self.ventana_juego:
            self.ventana_juego.tirada1.clear()
            self.ventana_juego.tirada2.clear()
            self.ventana_juego.tirada3.clear()