from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class Estilo:
    def __init__(self, ui):
        self.ui = ui
        self.dados_labels = [
            self.ui.dado1,
            self.ui.dado2,
            self.ui.dado3,
            self.ui.dado4,
            self.ui.dado5,
        ]
        self.configurar_tamano_dados()
        self.configurar_tamano_tiradas()
        self.dado_imagenes = self.cargar_rutas_imagenes()

    def configurar_tamano_dados(self):
        for lbl in self.dados_labels:
            lbl.setMinimumSize(50, 50)
            lbl.setMaximumSize(80, 80)

    def configurar_tamano_tiradas(self):
        tirada_labels = [self.ui.tirada1, self.ui.tirada2, self.ui.tirada3]
        for label in tirada_labels:
            label.setMinimumSize(50, 50)
            label.setMaximumSize(50, 50)
            label.setScaledContents(True)

    def cargar_rutas_imagenes(self):
        base_path = "recursos/img/"
        return [f"{base_path}dado{i}.png" for i in range(1, 7)]

    def mostrar_dados(self, dados):
        for i, valor_dado in enumerate(dados):
            if valor_dado is not None:
                pixmap = QPixmap(self.dado_imagenes[valor_dado - 1])
                scaled_pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio)
                self.dados_labels[i].setPixmap(scaled_pixmap)

    def actualizar_imagen_tirada(self, tiradas_restantes):
        base_path = "recursos/img/"
        imagenes_tiradas = [
            f"{base_path}tirada1.png",
            f"{base_path}tirada2.png",
            f"{base_path}tirada3.png"
        ]
        tiradas_labels = [self.ui.tirada1, self.ui.tirada2, self.ui.tirada3]
        tirada_actual = 3 - tiradas_restantes

        if 0 <= tirada_actual < len(imagenes_tiradas):
            pixmap = QPixmap(imagenes_tiradas[tirada_actual])
            #scaled_pixmap = pixmap.scaled(50, 50, Qt.KeepAspectRatio)
            tiradas_labels[tirada_actual].setPixmap(pixmap)
            tiradas_labels[tirada_actual].setAlignment(Qt.AlignCenter)

    def aplicar_estilo_seleccionado(self, indice_dado, seleccionado):
        estilo = "border: 2px solid red;" if seleccionado else "border: none;"
        self.dados_labels[indice_dado].setStyleSheet(estilo)

    def resetear_estilos_dados(self):
        for lbl in self.dados_labels:
            lbl.setStyleSheet("border: none;")

    def limpiar_dados(self):
        for lbl in self.dados_labels:
            lbl.clear()

    def limpiar_tiradas(self):
        self.ui.tirada1.clear()
        self.ui.tirada2.clear()
        self.ui.tirada3.clear()