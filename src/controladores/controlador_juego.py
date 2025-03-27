import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem
from PySide6.QtCore import Qt, QTimer
from vista.pantalla_juego import Ui_MainWindow
from modelo.dado import Dado
from modelo.categoria import Categoria
from modelo.turno import Turno
from modelo.puntaje import Puntaje
from vista.estilo_pantalla_juego import Estilo
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.seleccionados = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.dados = [Dado() for _ in range(5)]
        self.categoria = Categoria()
        self.puntaje = Puntaje(["Jugador 1", "Jugador 2"])
        self.turno = Turno("Jugador 1")
        self.ui.Tiradas_agotadas.hide()

        self.estilo = Estilo(self.ui)

        # Conectar eventos de los dados
        for i, lbl in enumerate(self.estilo.dados_labels):
            lbl.mousePressEvent = lambda event, idx=i: self.alternar_seleccion_dado(idx)

        # Conectar botones
        self.ui.lanzar_dados.clicked.connect(self.lanzar_dados)
        self.conectar_botones_categoria()

        # Configurar el temporizador
        self.temporizador = QTimer(self)
        self.temporizador.timeout.connect(self.actualizar_tiempo)

        # Iniciar el primer turno
        self.actualizar_jugador_actual()
        self.iniciar_turno()

    def conectar_botones_categoria(self):
        categorias = [
            (self.ui.uno, "1"), (self.ui.dos, "2"), (self.ui.tres, "3"), (self.ui.cuatro, "4"),
            (self.ui.cinco, "5"), (self.ui.seis, "6"), (self.ui.escalera, "Escalera"),
            (self.ui.full, "Full"), (self.ui.poker, "Póker"), (self.ui.generala, "Generala"),
            (self.ui.generala_doble, "Doble Generala")
        ]
        for boton, categoria in categorias:
            boton.clicked.connect(lambda _, cat=categoria: self.seleccionar_categoria(cat))

    def habilitar_botones_categoria(self, habilitar: bool):
        botones = [
            self.ui.uno, self.ui.dos, self.ui.tres, self.ui.cuatro, self.ui.cinco, self.ui.seis,
            self.ui.escalera, self.ui.full, self.ui.poker, self.ui.generala, self.ui.generala_doble
        ]
        for boton in botones:
            boton.setEnabled(habilitar)

    def iniciar_turno(self):
        self.actualizar_jugador_actual()
        self.ui.lanzar_dados.setEnabled(True)
        self.temporizador.start(1000)
        self.ui.tiempo_restante.setText(f"Tiempo: {self.turno.obtener_tiempo_restante()}s")
        self.habilitar_botones_categoria(False)
        self.reiniciar_interfaz()
        self.resetear_seleccion_dados()
        logging.info("Turno iniciado y dados reseteados.")

    def lanzar_dados(self):
        if self.turno.obtener_tiradas_restantes() == 0:
            self.ui.lanzar_dados.setEnabled(False)
            return

        dados = [self.dados[i].lanzar() if not self.seleccionados[i] else self.dados[i].obtener_valor() for i in
                 range(5)]
        self.estilo.mostrar_dados(dados)

        self.manejar_tiradas_restantes()

        self.habilitar_botones_categoria(True)

    def manejar_tiradas_restantes(self):
        self.estilo.actualizar_imagen_tirada(self.turno.obtener_tiradas_restantes())

        self.turno.disminuir_tiradas_restantes()
        logging.info(f"Lanzamientos restantes: {self.turno.obtener_tiradas_restantes()}")

        if self.turno.obtener_tiradas_restantes() == 0:
            self.ui.lanzar_dados.setEnabled(False)
            self.ui.Tiradas_agotadas.show()

    def alternar_seleccion_dado(self, indice_dado):
        self.seleccionados[indice_dado] = not self.seleccionados[indice_dado]
        self.estilo.aplicar_estilo_seleccionado(indice_dado, self.seleccionados[indice_dado])
        logging.info(f"Dado {indice_dado + 1} seleccionado: {self.seleccionados[indice_dado]}")

    def resetear_seleccion_dados(self):
        self.seleccionados = [False] * 5
        self.estilo.resetear_estilos_dados()
        logging.info("Selección de dados reseteada.")

    def pasar_turno(self):
        self.temporizador.stop()
        siguiente_jugador = "Jugador 2" if self.turno.obtener_jugador_actual() == "Jugador 1" else "Jugador 1"
        self.turno.reiniciar_turno(siguiente_jugador)
        self.turno.reiniciar_tiradas_restantes()
        self.actualizar_jugador_actual()
        self.ui.tiempo_restante.setText(f"Tiempo: {self.turno.obtener_tiempo_restante()}s")
        self.temporizador.start(1000)
        self.ui.lanzar_dados.setEnabled(True)
        self.reiniciar_interfaz()
        self.resetear_seleccion_dados()
        self.ui.Tiradas_agotadas.hide()

        logging.info(f"Turno pasado. Ahora juega: {self.turno.obtener_jugador_actual()}")

    def seleccionar_categoria(self, categoria: str):
        try:
            dados = [self.dados[i].obtener_valor() for i in range(5)]
            ha_marcado_generala = "Generala" in self.puntaje.obtener_categorias_usadas(self.turno.obtener_jugador_actual())
            puntos = self.categoria.calcular_puntos(dados, categoria, ha_marcado_generala)
            self.puntaje.registrar_puntos(self.turno.obtener_jugador_actual(), puntos, categoria)
            self.actualizar_tabla_puntajes()
            self.reiniciar_interfaz()
            self.resetear_seleccion_dados()
            self.pasar_turno()
            self.habilitar_botones_categoria(False)
            self.ui.lanzar_dados.setEnabled(True)
        except ValueError as e:
            QMessageBox.information(self, "Error", str(e))

    def reiniciar_interfaz(self):
        self.estilo.limpiar_dados()
        self.estilo.limpiar_tiradas()
        self.resetear_seleccion_dados()
        logging.info("Interfaz reiniciada.")

    def actualizar_tabla_puntajes(self):
        jugador_actual = self.turno.obtener_jugador_actual()
        indice_jugador = 0 if jugador_actual == "Jugador 1" else 1
        categorias = ["1", "2", "3", "4", "5", "6", "Escalera", "Full", "Póker", "Generala", "Doble Generala"]

        for j, categoria in enumerate(categorias):
            if categoria in self.puntaje.obtener_categorias_usadas(jugador_actual):
                puntos = self.puntaje.obtener_puntaje_categoria(jugador_actual, categoria)
                item = QTableWidgetItem(str(puntos))
                item.setTextAlignment(Qt.AlignCenter)
                self.ui.tabla_puntajes.setItem(j, indice_jugador, item)
            else:
                self.ui.tabla_puntajes.setItem(j, indice_jugador, QTableWidgetItem(""))

        puntaje_total = self.puntaje.obtener_puntaje_jugador(jugador_actual)
        item_total = QTableWidgetItem(str(puntaje_total))
        item_total.setTextAlignment(Qt.AlignCenter)
        self.ui.tabla_puntajes.setItem(len(categorias), indice_jugador, item_total)

    def finalizar_juego(self):
        ganador = self.puntaje.determinar_ganador()
        QMessageBox.information(self, "Juego terminado", f"¡Juego terminado! El ganador es {ganador}")
        self.ui.lanzar_dados.setEnabled(False)
        self.habilitar_botones_categoria(False)

    def actualizar_tiempo(self):
        tiempo_restante = self.turno.disminuir_tiempo()
        self.ui.tiempo_restante.setText(f"Tiempo: {tiempo_restante}s")

        if self.turno.tiempo_agotado():
            self.temporizador.stop()
            self.turno.pasar_turno_si_el_tiempo_se_agotado(self.puntaje, self.actualizar_tabla_puntajes)  # Pasar la función de actualización
            self.pasar_turno()

    def actualizar_jugador_actual(self):
        self.ui.jugador_actual.setText(f"Turno de: {self.turno.obtener_jugador_actual()}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())




