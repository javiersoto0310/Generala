# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'pantalla_conexion.ui'
##
## Created by: Qt User Interface Compiler version 6.8.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLineEdit, QMainWindow, QMenuBar,
    QPushButton, QSizePolicy, QStatusBar, QTextEdit,
    QVBoxLayout, QWidget)

class Conexion(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(408, 331)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.entrada_nombre = QLineEdit(self.centralwidget)
        self.entrada_nombre.setObjectName(u"entrada_nombre")

        self.verticalLayout.addWidget(self.entrada_nombre)

        self.area_mensajes = QTextEdit(self.centralwidget)
        self.area_mensajes.setObjectName(u"area_mensajes")

        self.verticalLayout.addWidget(self.area_mensajes)

        self.btn_crear_sala = QPushButton(self.centralwidget)
        self.btn_crear_sala.setObjectName(u"btn_crear_sala")

        self.verticalLayout.addWidget(self.btn_crear_sala)

        self.btn_unirse_a_sala = QPushButton(self.centralwidget)
        self.btn_unirse_a_sala.setObjectName(u"btn_unirse_a_sala")

        self.verticalLayout.addWidget(self.btn_unirse_a_sala)

        self.entrada_id_sala = QLineEdit(self.centralwidget)
        self.entrada_id_sala.setObjectName(u"entrada_id_sala")

        self.verticalLayout.addWidget(self.entrada_id_sala)

        self.btn_listar_salas = QPushButton(self.centralwidget)
        self.btn_listar_salas.setObjectName(u"btn_listar_salas")

        self.verticalLayout.addWidget(self.btn_listar_salas)

        self.btn_ranking = QPushButton(self.centralwidget)
        self.btn_ranking.setObjectName(u"btn_ranking")

        self.verticalLayout.addWidget(self.btn_ranking)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 408, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Conexi\u00f3n en red", None))
        self.entrada_nombre.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Ingrese su nombre", None))
        self.btn_crear_sala.setText(QCoreApplication.translate("MainWindow", u"Crear Sala", None))
        self.btn_unirse_a_sala.setText(QCoreApplication.translate("MainWindow", u"Unirse a Sala", None))
        self.entrada_id_sala.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Ingrese ID de la sala", None))
        self.btn_listar_salas.setText(QCoreApplication.translate("MainWindow", u"Listar Salas Disponibles", None))
        self.btn_ranking.setText(QCoreApplication.translate("MainWindow", u"Ranking", None))
    # retranslateUi

