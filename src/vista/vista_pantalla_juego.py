import logging

from PySide6.QtCore import QTimer
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QMainWindow, QPushButton, QLabel, QTableWidgetItem, QAbstractItemView, QHeaderView, QTableWidget, QMessageBox
from vista.pantalla_juego import PantallaJuego
from vista.estilo_pantalla_juego import Estilo


class JuegoVentana(QMainWindow, PantallaJuego):
    mostrar_ganador_signal = Signal(str, dict)

    def __init__(self, controlador=None):
        super().__init__()
        super().setupUi(self)

        self.controlador = controlador
        self.estilo = Estilo(self)
        self._elementos_basicos_ui()
        self._componentes()
        self._inicializacion_del_estado_del_juego()
        self.mostrar_ganador_signal.connect(self._mostrar_dialogo_ganador)

    def _mostrar_dialogo_ganador(self, ganador, puntajes):
        mensaje = "Resultado final:\n\n"
        for jugador, puntos in puntajes.items():
            mensaje += f"{jugador}: {puntos} puntos\n"

        if ganador:
            mensaje += f"\n Ganador: {ganador}"
        else:
            mensaje += "\n  ¡Empate!"

        QMessageBox.information(self, "Fin del Juego", mensaje)

    def _elementos_basicos_ui(self):
        for tirada in [self.tirada1, self.tirada2, self.tirada3]:
            tirada.setVisible(False)
            tirada.raise_()
            tirada.setStyleSheet("background: transparent; border: none;")
            logging.debug(f"Tirada {tirada} configurada")

        self.label_jugador_actual = self.findChild(QLabel, 'jugador_actual')
        self.lanzar_dados_btn = self.findChild(QPushButton, 'lanzar_dados')
        self.Tiradas_agotadas_label = self.findChild(QLabel, 'Tiradas_agotadas')
        self.tabla_puntajes = self.findChild(QTableWidget, 'tabla_puntajes')

        if not self.label_jugador_actual:
            logging.error("QLabel 'jugador_actual' no encontrado")

        if self.lanzar_dados_btn:
            self.lanzar_dados_btn.setEnabled(False)

        if self.Tiradas_agotadas_label:
            self.Tiradas_agotadas_label.setText("")

    def _componentes(self):
        self.configurar_tabla_puntajes()

    def _inicializacion_del_estado_del_juego(self):
        self.configurar_clicks_dados()
        self.conectar_botones_categorias()
        self.deshabilitar_categorias()

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
            logging.warning("No se pudo determinar el jugador actual para el mensaje de tiradas agotadas.")

    def configurar_clicks_dados(self):
        for i, dado_label in enumerate(self.estilo.dados_labels):
            if dado_label:
                dado_label.mousePressEvent = lambda event, idx=i: self.seleccionar_dado_para_bloqueo(idx)
                logging.debug(f"Click configurado para el dado {i}.")

    def seleccionar_dado_para_bloqueo(self, indice_dado):
        if self.controlador and hasattr(self.controlador, 'tiradas_restantes'):
            if self.controlador.tiradas_restantes < 3:
                self.controlador.dados_bloqueados[indice_dado] = not self.controlador.dados_bloqueados[indice_dado]
                self.estilo.aplicar_estilo_seleccionado(indice_dado, self.controlador.dados_bloqueados[indice_dado])
                logging.info(f"Dado {indice_dado} bloqueado: {self.controlador.dados_bloqueados[indice_dado]}")
            else:
                logging.debug("Intento de bloquear dado antes de la primera tirada.")

    def habilitar_boton_lanzar(self):
        if self.lanzar_dados_btn:
            self.lanzar_dados_btn.setEnabled(True)
            logging.info("Botón lanzar habilitado")
        else:
            logging.warning("Botón lanzar no encontrado al intentar habilitar.")

    def deshabilitar_boton_lanzar(self):
        if self.lanzar_dados_btn:
            self.lanzar_dados_btn.setEnabled(False)
            logging.info("Botón lanzar deshabilitado")
        else:
            logging.warning("Botón lanzar no encontrado al intentar deshabilitar.")

    def actualizar_jugador_actual(self, nombre_jugador: str):
        if not hasattr(self, 'label_jugador_actual') or self.label_jugador_actual is None:
            logging.error("QLabel 'jugador_actual' no encontrado o es None")
            return

        nuevo_nombre_jugador = f"Turno de: {nombre_jugador}"
        self.label_jugador_actual.setText(nuevo_nombre_jugador)
        logging.info(f"Nombre del jugador actualizado a: '{nuevo_nombre_jugador}'")

        if self.controlador and hasattr(self.controlador, 'jugador_actual'):
            try:
                jugador_local = self.controlador.jugador_actual.obtener_nombre()
                es_mi_turno = (nombre_jugador == jugador_local)
                tirada_realizada = getattr(self.controlador, 'tirada_realizada', False)

                if es_mi_turno and tirada_realizada:
                    self.habilitar_categorias()
                    logging.debug("Categorías habilitadas (turno local con tirada)")
                else:
                    self.deshabilitar_categorias()
                    logging.debug("Categorías deshabilitadas (turno oponente o sin tirada)")

            except AttributeError as e:
                logging.error(f"Error al verificar jugador: {str(e)}")
                self.deshabilitar_categorias()
        else:
            logging.warning("Controlador no disponible para gestión de categorías")
            self.deshabilitar_categorias()

    def actualizar_dados_lanzados(self, jugador_sid, resultados):
        if not resultados:
            logging.warning("Resultados de lanzamiento vacíos.")
            return

        self.estilo.mostrar_dados(resultados)
        logging.info(f"Dados mostrados: {resultados}")

        if hasattr(self.controlador, 'tiradas_restantes'):
            self.estilo.actualizar_imagen_tirada(self.controlador.tiradas_restantes)

        if (hasattr(self.controlador, 'jugador_actual') and
                hasattr(self.controlador, 'nombre_jugador_actual') and
                jugador_sid != self.controlador.jugador_actual.obtener_nombre()):
            self.label_jugador_actual.setText(f"Turno de: {jugador_sid}")
            self.deshabilitar_boton_lanzar()
            logging.info(f"Mostrando resultados del jugador {jugador_sid}, botón lanzar deshabilitado.")

    def habilitar_categorias(self):
        if self.controlador and self.controlador.jugador_actual:
            jugador_local = self.controlador.jugador_actual.obtener_nombre()
            jugador_actual = self.controlador.turno.obtener_jugador_actual()

            if jugador_local == jugador_actual:
                if hasattr(self.controlador, 'categoria'):
                    disponibles = self.controlador.categoria.obtener_categorias_disponibles(jugador_local)
                    self.habilitar_categorias_disponibles(disponibles)
                else:
                    logging.warning("Controlador no tiene 'categoria'")

    def deshabilitar_categorias(self):
        for btn in [self.uno, self.dos, self.tres, self.cuatro,
                    self.cinco, self.seis, self.escalera, self.full,
                    self.poker, self.generala, self.generala_doble]:
            btn.setEnabled(False)
        logging.debug("Categorías deshabilitadas.")

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
        if not (self.controlador and hasattr(self.controlador,'tirada_realizada')) or not self.controlador.tirada_realizada:
            logging.warning(f"Intento de seleccionar categoría {categoria} antes de la primera tirada.")
            return

        self.deshabilitar_boton_lanzar()
        self.deshabilitar_categorias()
        self.Tiradas_agotadas_label.setText("")

        try:
            jugador_local = self.controlador.jugador_actual.obtener_nombre()
            jugador_turno_actual = self.controlador.turno.obtener_jugador_actual()

            if jugador_local != jugador_turno_actual:
                logging.warning(f"Intento de seleccionar categoría {categoria} fuera de turno.")
                return

            logging.info(f"Jugador {jugador_local} seleccionó la categoría: {categoria}")

            puntos = self.controlador.calcular_puntos_para_categoria(
                dados=self.controlador.dados_actuales,
                categoria=categoria
            )
            logging.info(f"Puntos calculados para {categoria}: {puntos}")

            if not self.ha_terminado_juego(self.controlador.jugador_actual.obtener_nombre()):
                self.controlador.pasar_turno()

        except Exception as e:
            logging.error(f"Error al seleccionar categoría {categoria}: {str(e)}", exc_info=True)
            self.deshabilitar_boton_lanzar()
            self.deshabilitar_categorias()

    def ha_terminado_juego(self, jugador_nombre: str) -> bool:
        categorias = [
            "1", "2", "3", "4", "5", "6",
            "Escalera", "Full", "Póker", "Generala", "Doble Generala"
        ]
        return all(self.ha_marcado_categoria(jugador_nombre, cat) for cat in categorias)

    def actualizar_tabla_puntajes(self, puntajes: dict):
        try:
            categoria_a_fila = {
                "1": 0, "2": 1, "3": 2, "4": 3, "5": 4, "6": 5,
                "Escalera": 6, "Full": 7, "Póker": 8,
                "Generala": 9, "Doble Generala": 10
            }

            if not hasattr(self, 'tabla_puntajes') or self.tabla_puntajes is None:
                logging.error("Error: tabla_puntajes no inicializada")
                return

            self.tabla_puntajes.clearContents()
            self.tabla_puntajes.setRowCount(12)
            self.tabla_puntajes.setColumnCount(len(puntajes))

            jugador_a_columna = {}
            if self.controlador and hasattr(self.controlador, 'jugadores'):
                for i, jugador in enumerate(self.controlador.jugadores):
                    jugador_a_columna[jugador.obtener_nombre()] = i
            else:
                for i, jugador in enumerate(puntajes.keys()):
                    jugador_a_columna[jugador] = i

            for jugador, categorias in puntajes.items():
                columna = jugador_a_columna.get(jugador)
                if columna is None:
                    logging.error(f"Jugador {jugador} no encontrado en la lista de jugadores.")
                    continue
                for categoria, puntos in categorias.items():
                    fila = categoria_a_fila.get(categoria)
                    if fila is not None:
                        item = QTableWidgetItem(str(puntos))
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tabla_puntajes.setItem(fila, columna, item)
                        logging.debug(f"Puntaje {puntos} para {jugador} en {categoria} colocado en la tabla. Fila: {fila}, Columna: {columna}")
                    else:
                        logging.error(f"Categoría {categoria} no encontrada en el mapeo de filas.")

            self.calcular_puntuacion_total()
            logging.debug("Puntuación total calculada.")
            self.tabla_puntajes.viewport().update()

        except Exception as e:
            logging.error(f"Error al actualizar tabla: {str(e)}")

    def calcular_puntuacion_total(self):
        if not hasattr(self, 'tabla_puntajes') or self.tabla_puntajes is None:
            logging.warning("Tabla de puntajes no inicializada al calcular la puntuación total.")
            return

        for columna in range(self.tabla_puntajes.columnCount()):
            total = 0
            for fila in range(11):
                item = self.tabla_puntajes.item(fila, columna)
                if item and item.text().isdigit():
                    total += int(item.text())

            total_item = QTableWidgetItem(str(total))
            total_item.setTextAlignment(Qt.AlignCenter)
            self.tabla_puntajes.setItem(11, columna, total_item)
            logging.debug(f"Puntuación total {total} colocada en la columna {columna}.")

    def configurar_tabla_puntajes(self, nombres_jugadores=None):
        if not hasattr(self, 'tabla_puntajes') or self.tabla_puntajes is None:
            logging.error("Error: tabla_puntajes no inicializada")
            return

        if nombres_jugadores is None:
             if self.controlador and hasattr(self.controlador, 'jugadores'):
                nombres_jugadores = [j.obtener_nombre() for j in self.controlador.jugadores]
             else:
                nombres_jugadores = ["Jugador 1", "Jugador 2"]

        self.tabla_puntajes.setRowCount(12)
        self.tabla_puntajes.setColumnCount(len(nombres_jugadores))

        for i, nombre_jugador in enumerate(nombres_jugadores):
            self.tabla_puntajes.setHorizontalHeaderItem(i, QTableWidgetItem(nombre_jugador))

        self.tabla_puntajes.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla_puntajes.setSelectionMode(QAbstractItemView.NoSelection)
        self.tabla_puntajes.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_puntajes.verticalHeader().setVisible(False)
        self.tabla_puntajes.viewport().update()
        logging.info("Tabla de puntajes configurada")

    def ha_marcado_categoria(self, jugador: str, categoria: str) -> bool:
        if not hasattr(self, 'tabla_puntajes') or self.tabla_puntajes is None:
            return False

        categoria_a_fila = {
            "1": 0, "2": 1, "3": 2, "4": 3, "5": 4, "6": 5,
            "Escalera": 6, "Full": 7, "Póker": 8,
            "Generala": 9, "Doble Generala": 10
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

        return item is not None

    def manejar_cambio_turno(self, data):
        try:
            if not isinstance(data, dict):
                logging.error("Datos de cambio de turno inválidos")
                return

            jugador_nombre = data.get('jugador_nombre') or data.get('jugador', '')
            es_mi_turno = data.get('es_mi_turno', False)
            es_inicio = data.get('es_inicio', False)

            if not jugador_nombre:
                logging.error("Datos incompletos: falta nombre del jugador")
                return

            self.actualizar_jugador_actual(jugador_nombre)

            if es_inicio or not getattr(self.controlador, 'tirada_realizada', True):
                if hasattr(self, 'estilo'):
                    self.estilo.limpiar_tiradas()
                if hasattr(self, 'Tiradas_agotadas_label'):
                    self.Tiradas_agotadas_label.setText("")

            if es_mi_turno:
                self.deshabilitar_categorias()
                self.habilitar_boton_lanzar()

                if es_inicio:
                    self.controlador.resetear_tiradas()
            else:
                self.deshabilitar_boton_lanzar()
                self.deshabilitar_categorias()

        except Exception as e:
            logging.error(f"Error al manejar_cambio_turno: {str(e)}")
            if hasattr(self, 'Tiradas_agotadas_label'):
                self.Tiradas_agotadas_label.setText("Error en cambio de turno")
            self.deshabilitar_boton_lanzar()
            self.deshabilitar_categorias()

    def limpiar_interfaz_turno(self):
        self.estilo.limpiar_dados()
        self.estilo.limpiar_tiradas()
        if hasattr(self, 'Tiradas_agotadas_label'):
            self.Tiradas_agotadas_label.setText("")
        self.estilo.resetear_estilos_dados()

    def reiniciar_interfaz_juego(self):
        self.limpiar_interfaz_turno()

        if hasattr(self, 'tabla_puntajes') and self.tabla_puntajes:
            self.tabla_puntajes.clearContents()

        if hasattr(self, 'Tiradas_agotadas_label'):
            self.Tiradas_agotadas_label.setText("")

        if hasattr(self, 'label_jugador_actual'):
            self.label_jugador_actual.setText("Esperando turno...")

        self.deshabilitar_boton_lanzar()
        self.deshabilitar_categorias()
        self.estilo.limpiar_dados()
        self.estilo.limpiar_tiradas()
        self.estilo.resetear_estilos_dados()

    def habilitar_categorias_disponibles(self, disponibles: list):
        mapeo = {
            "1": self.uno, "2": self.dos, "3": self.tres, "4": self.cuatro,
            "5": self.cinco, "6": self.seis, "Escalera": self.escalera,
            "Full": self.full, "Póker": self.poker,
            "Generala": self.generala, "Doble Generala": self.generala_doble
        }

        for nombre, boton in mapeo.items():
            boton.setEnabled(nombre in disponibles)

    def mostrar_ganador(self, ganador, puntajes: dict):
        self.mostrar_ganador_signal.emit(ganador, puntajes)

    def closeEvent(self, event):
        dialogo = QMessageBox(self)
        dialogo.setWindowTitle("Confirmar salida")
        dialogo.setText("¿Deseas abandonar la partida?\nSe cerrará automáticamente en 10 segundos.")
        boton_si = dialogo.addButton("Sí", QMessageBox.AcceptRole)
        boton_no = dialogo.addButton("No", QMessageBox.RejectRole)
        dialogo.setDefaultButton(boton_no)

        temporizador = QTimer(self)
        temporizador.setInterval(10000)
        temporizador.setSingleShot(True)
        temporizador.timeout.connect(lambda: dialogo.done(0))
        temporizador.start()

        respuesta = dialogo.exec()

        if respuesta == 0:
            if self.controlador.cliente:
                self.controlador.cliente.disconnect()
            event.accept()

        elif dialogo.clickedButton() == boton_si:
            if self.controlador.cliente:
                self.controlador.cliente.disconnect()
            event.accept()

        else:
            event.ignore()



