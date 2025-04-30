from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QPushButton, QLabel, QTableWidgetItem, QAbstractItemView, QHeaderView
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

        self.configurar_handlers()
        logging.info("Ventana de juego inicializada correctamente")

        if controlador:
            controlador.mostrar_resultados_lanzamiento.connect(self.actualizar_dados_lanzados)
            controlador.actualizar_tiradas_restantes.connect(self.estilo.actualizar_imagen_tirada)
            controlador.actualizar_tiradas_restantes.connect(self.actualizar_mensaje_tiradas_agotadas)

        if controlador:
            controlador.habilitar_categorias.connect(self.habilitar_categorias)
            controlador.deshabilitar_categorias.connect(self.deshabilitar_categorias)

        self.deshabilitar_categorias()

        self.conectar_botones_categorias()

        self.configurar_tabla_puntajes()

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

        if self.controlador and hasattr(self.controlador, 'jugador_actual'):
            try:
                jugador_local = self.controlador.jugador_actual.obtener_nombre()

                if (nombre_jugador == jugador_local and
                        hasattr(self.controlador, 'tirada_realizada') and
                        self.controlador.tirada_realizada):
                    self.habilitar_categorias()
                else:
                    self.deshabilitar_categorias()

            except AttributeError as e:
                logging.error(f"Error al actualizar jugador actual: {str(e)}")
                self.deshabilitar_categorias()
        else:
            self.deshabilitar_categorias()

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

    def habilitar_categorias(self):
        if self.controlador and self.controlador.jugador_actual:
            jugador_local = self.controlador.jugador_actual.obtener_nombre()
            jugador_actual = self.controlador.turno.obtener_jugador_actual()

            if jugador_local == jugador_actual:
                for btn in [self.uno, self.dos, self.tres, self.cuatro,
                            self.cinco, self.seis, self.escalera, self.full,
                            self.poker, self.generala, self.generala_doble]:
                    btn.setEnabled(True)

    def deshabilitar_categorias(self):
        for btn in [self.uno, self.dos, self.tres, self.cuatro,
                    self.cinco, self.seis, self.escalera, self.full,
                    self.poker, self.generala, self.generala_doble]:
            btn.setEnabled(False)

    def conectar_botones_categorias(self):
        self.uno.clicked.connect(lambda: self.seleccionar_categoria("1"))
        self.dos.clicked.connect(lambda: self.seleccionar_categoria("2"))
        self.tres.clicked.connect(lambda: self.seleccionar_categoria("3"))
        self.cuatro.clicked.connect(lambda: self.seleccionar_categoria("4"))
        self.cinco.clicked.connect(lambda: self.seleccionar_categoria("5"))
        self.seis.clicked.connect(lambda: self.seleccionar_categoria("6"))
        self.escalera.clicked.connect(lambda: self.seleccionar_categoria("Escalera"))
        self.full.clicked.connect(lambda: self.seleccionar_categoria("Full"))
        self.poker.clicked.connect(lambda: self.seleccionar_categoria("Póker"))
        self.generala.clicked.connect(lambda: self.seleccionar_categoria("Generala"))
        self.generala_doble.clicked.connect(lambda: self.seleccionar_categoria("Doble Generala"))

    def seleccionar_categoria(self, categoria: str):
        if not (self.controlador and hasattr(self.controlador, 'tirada_realizada')) \
                or not self.controlador.tirada_realizada:
            return

        try:
            jugador_local = self.controlador.jugador_actual.obtener_nombre()
            jugador_turno_actual = self.controlador.turno.obtener_jugador_actual()

            if jugador_local != jugador_turno_actual:
                return

            puntos = self.controlador.calcular_puntos_para_categoria(
                dados=self.controlador.dados_actuales,
                categoria=categoria
            )

            self.actualizar_tabla_puntajes(self.controlador.puntaje.obtener_puntajes())

            self.controlador.pasar_turno()

        except (AttributeError, ValueError) as e:
            logging.error(f"Error al seleccionar categoría: {str(e)}")

    def actualizar_tabla_puntajes(self, puntajes: dict):
        try:
            categoria_a_fila = {
                "1": 0, "2": 1, "3": 2, "4": 3, "5": 4, "6": 5,
                "Escalera": 6, "Full": 7, "Póker": 8,
                "Generala": 9, "Doble Generala": 10
            }

            for i in range(self.tabla_puntajes.rowCount()):
                for j in range(self.tabla_puntajes.columnCount()):
                    self.tabla_puntajes.setItem(i, j, QTableWidgetItem(""))

            for jugador, categorias in puntajes.items():
                columna = 0 if jugador == self.controlador.jugadores[0].obtener_nombre() else 1
                for categoria, puntos in categorias.items():
                    fila = categoria_a_fila.get(categoria)
                    if fila is not None:
                        item = QTableWidgetItem(str(puntos))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tabla_puntajes.setItem(fila, columna, item)

            self.calcular_puntuacion_total()
            self.tabla_puntajes.viewport().update()

        except Exception as e:
            logging.error(f"Error al actualizar tabla: {str(e)}")

    def calcular_puntuacion_total(self):
        if not hasattr(self, 'tabla_puntajes'):
            return

        for col in range(self.tabla_puntajes.columnCount()):
            total = 0
            for row in range(11):
                item = self.tabla_puntajes.item(row, col)
                if item and item.text().isdigit():
                    total += int(item.text())

            total_item = QTableWidgetItem(str(total))
            total_item.setTextAlignment(Qt.AlignCenter)
            self.tabla_puntajes.setItem(11, col, total_item)

    def configurar_tabla_puntajes(self, nombres_jugadores=None):
        if not hasattr(self, 'tabla_puntajes'):
            return

        if nombres_jugadores and len(nombres_jugadores) >= 2:
            nombre_jugador1, nombre_jugador2 = nombres_jugadores[:2]
        elif hasattr(self, 'controlador') and self.controlador:
            nombre_jugador1 = "Jugador 1"
            nombre_jugador2 = "Jugador 2"

            if hasattr(self.controlador, 'jugadores'):
                if len(self.controlador.jugadores) > 0:
                    nombre_jugador1 = self.controlador.jugadores[0].obtener_nombre()
                if len(self.controlador.jugadores) > 1:
                    nombre_jugador2 = self.controlador.jugadores[1].obtener_nombre()
        else:
            nombre_jugador1 = "Jugador 1"
            nombre_jugador2 = "Jugador 2"

        if self.tabla_puntajes.columnCount() < 2:
            self.tabla_puntajes.setColumnCount(2)

        self.tabla_puntajes.setHorizontalHeaderItem(0, QTableWidgetItem(nombre_jugador1))
        self.tabla_puntajes.setHorizontalHeaderItem(1, QTableWidgetItem(nombre_jugador2))
        self.tabla_puntajes.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla_puntajes.setSelectionMode(QAbstractItemView.NoSelection)
        self.tabla_puntajes.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_puntajes.viewport().update()

    def ha_marcado_categoria(self, jugador: str, categoria: str) -> bool:
        if not hasattr(self, 'tabla_puntajes'):
            return False

        categoria_a_fila = {
            "1": 0, "2": 1, "3": 2, "4": 3, "5": 4, "6": 5,
            "Escalera": 6, "Full": 7, "Póker": 8,
            "Generala": 9, "Generala Doble": 10
        }

        fila = categoria_a_fila.get(categoria, -1)
        if fila == -1:
            return False

        jugadores = []
        if hasattr(self, 'controlador') and hasattr(self.controlador, 'jugadores'):
            jugadores = [j.obtener_nombre() for j in self.controlador.jugadores]

        if jugador not in jugadores:
            return False

        columna = jugadores.index(jugador)
        item = self.tabla_puntajes.item(fila, columna)

        return item is not None and item.text().isdigit() and int(item.text()) > 0

    def configurar_handlers(self):
        if self.controlador and hasattr(self.controlador, 'cliente'):
            @self.controlador.cliente.on('actualizar_puntajes')
            def on_actualizar_puntajes(data):
                logging.info(
                    f"Recibido 'actualizar_puntajes' - Sala ID recibido: {data.get('sala_id')}, Sala ID local: {self.controlador.sala_id_actual}")
                if data.get('sala_id') == self.controlador.sala_id_actual:
                    self.actualizar_tabla_puntajes(data['puntajes'])