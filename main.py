import logging
import sys
from typing import Optional, List

from PySide6.QtWidgets import QApplication, QMainWindow, QListWidgetItem
from PySide6.QtCore import QObject, Qt

from src.vista.pantalla_conexion import Conexion
from src.controladores.controlador_salas import ControladorSalas
from src.controladores.controlador_juego import ControladorJuego
from src.vista.vista_pantalla_juego import JuegoVentana


class MainApp(QObject):
    controlador_salas: ControladorSalas
    controlador_juego: ControladorJuego
    ventana_conexion: QMainWindow
    ventana_juego: Optional[JuegoVentana] = None

    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)

        self.ventana_conexion = QMainWindow()
        self.ui_conexion = Conexion()
        self.ui_conexion.setupUi(self.ventana_conexion)

        self.controlador_salas = ControladorSalas()
        self.controlador_juego = ControladorJuego()

        self.controlador_juego.set_cliente(self.controlador_salas.cliente)

        self.controlador_salas.ui = self.ui_conexion
        self.controlador_salas.controlador_juego = self.controlador_juego
        self.ui_conexion.btn_crear_sala.clicked.connect(self.crear_sala)
        self.ui_conexion.btn_unirse_a_sala.clicked.connect(self.unirse_a_sala_seleccionada)
        self.ui_conexion.btn_listar_salas.clicked.connect(self.solicitar_lista_salas)

        self.ventana_juego = JuegoVentana(self.controlador_juego)
        self.controlador_juego.set_vista(self.ventana_juego)
        self.ventana_juego.lanzar_dados_btn.clicked.connect(self.controlador_juego.lanzar_dados)
        self.controlador_juego.cambio_turno_signal.connect(self.ventana_juego.manejar_cambio_turno)
        self.controlador_juego.habilitar_lanzamiento.connect(self.ventana_juego.habilitar_boton_lanzar, Qt.QueuedConnection)
        self.controlador_juego.deshabilitar_lanzamiento.connect(self.ventana_juego.deshabilitar_boton_lanzar, Qt.QueuedConnection)
        self.controlador_juego.actualizar_tiradas_restantes.connect(self.ventana_juego.estilo.actualizar_imagen_tirada)
        self.controlador_juego.actualizar_tiradas_restantes.connect(self.ventana_juego.actualizar_mensaje_tiradas_agotadas)
        self.controlador_juego.mostrar_resultados_lanzamiento.connect(self.ventana_juego.actualizar_dados_lanzados, Qt.QueuedConnection)
        self.controlador_juego.habilitar_categorias.connect(self.ventana_juego.habilitar_categorias)
        self.controlador_juego.jugador_desconectado.connect(self.volver_a_pantalla_conexion_por_desconexion_del_oponente)

        self.controlador_salas.mostrar_juego.connect(self.mostrar_ventana_juego, Qt.QueuedConnection)
        self.controlador_salas.conexion_exitosa.connect(self.on_conexion_exitosa, Qt.QueuedConnection)
        self.controlador_salas.mostrar_salas.connect(self.mostrar_salas_en_lista)
        self.controlador_salas.error.connect(self.mostrar_error)
        self.controlador_salas.mostrar_mensaje.connect(self.mostrar_mensaje_area)

        self.ventana_conexion.show()
        sys.exit(self.app.exec())

    def mostrar_mensaje_area(self, mensaje: str):
        self.ui_conexion.area_mensajes.setText(mensaje)

    def mostrar_error(self, mensaje: str):
        self.ui_conexion.area_mensajes.setText(mensaje)

    def on_conexion_exitosa(self, datos_conexion: dict):
        self.ui_conexion.area_mensajes.setText("Conectado al servidor")
        self.controlador_juego.set_jugador_sid_local(datos_conexion['sid'])
        if datos_conexion['nombre_jugador']:
            self.controlador_salas.nombre_jugador_actual = datos_conexion['nombre_jugador']
        logging.info(f"Conexión establecida. SID: {datos_conexion['sid']}")

    def crear_sala(self):
        self.controlador_salas.crear_sala(
            nombre=self.ui_conexion.entrada_nombre.text().strip()
        )

    def unirse_a_sala_seleccionada(self):
        sala_seleccionada = self.ui_conexion.lista_salas_disponibles.currentItem()
        if not sala_seleccionada:
            self.mostrar_mensaje_area("Debe seleccionar una sala para unirse.")
            return

        self.controlador_salas.unirse_a_sala(
            sala_id=sala_seleccionada.data(Qt.UserRole),
            nombre=self.ui_conexion.entrada_nombre.text().strip()
        )

    def mostrar_salas_en_lista(self, lista_salas: List[dict]):
        self.ui_conexion.lista_salas_disponibles.clear()
        for sala in lista_salas:
            item = QListWidgetItem(f"{sala['sala_id']} - Jugadores: {', '.join(sala['jugadores'])}")
            item.setData(Qt.UserRole, sala['sala_id'])
            self.ui_conexion.lista_salas_disponibles.addItem(item)

    def solicitar_lista_salas(self):
        self.controlador_salas.listar_salas(
            nombre=self.ui_conexion.entrada_nombre.text().strip()
        )

    def mostrar_ventana_juego(self, sala_id: str, jugadores: List[str], primer_jugador: str):
        logging.info(f"Mostrando pantalla de juego para la sala: {sala_id}")
        self.ventana_conexion.hide()

        self.ventana_juego.setWindowTitle(f"Generala - Sala: {sala_id} - Jugador: {self.controlador_salas.nombre_jugador_actual}")
        self.ventana_juego.reiniciar_interfaz_juego()
        self.ventana_juego.configurar_tabla_puntajes(jugadores)
        self.controlador_juego.iniciar_partida(jugadores, self.controlador_salas.nombre_jugador_actual, sala_id=sala_id, primer_jugador=primer_jugador)

        self.ventana_juego.show()

    def volver_a_pantalla_conexion_por_desconexion_del_oponente(self, mensaje: str):
        self.ventana_juego.hide()
        self.ventana_conexion.show()
        self.ui_conexion.area_mensajes.setText(mensaje)
        self.ui_conexion.lista_salas_disponibles.clear()


if __name__ == "__main__":
    app = MainApp()