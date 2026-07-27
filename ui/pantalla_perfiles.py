"""Pantalla de perfiles: lista los perfiles guardados y permite agregar/eliminar."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from core.perfiles import GestorPerfiles
from .dialogo_nuevo_perfil import DialogoNuevoPerfil


class PantallaPerfiles(QWidget):
    volver = pyqtSignal()

    def __init__(self, gestor_perfiles: GestorPerfiles):
        super().__init__()
        self.gestor_perfiles = gestor_perfiles

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        cabecera = QHBoxLayout()
        boton_volver = QPushButton("←")
        boton_volver.setFixedWidth(36)
        boton_volver.clicked.connect(self.volver.emit)
        titulo = QLabel("Perfiles")
        titulo.setStyleSheet("font-size: 20px; font-weight: 600;")
        boton_agregar = QPushButton("+")
        boton_agregar.setFixedSize(36, 36)
        boton_agregar.setStyleSheet("font-size: 18px; background-color: #2563eb; color: white; border-radius: 18px;")
        boton_agregar.clicked.connect(self._agregar_perfil)

        cabecera.addWidget(boton_volver)
        cabecera.addWidget(titulo)
        cabecera.addStretch()
        cabecera.addWidget(boton_agregar)
        layout.addLayout(cabecera)

        self.lista = QListWidget()
        self.lista.setStyleSheet("QListWidget::item { padding: 10px; }")
        layout.addWidget(self.lista)

        boton_eliminar = QPushButton("Eliminar perfil seleccionado")
        boton_eliminar.clicked.connect(self._eliminar_seleccionado)
        layout.addWidget(boton_eliminar)

        self.recargar()

    def recargar(self):
        self.lista.clear()
        for perfil in self.gestor_perfiles.listar_perfiles():
            vigente_hasta = perfil.info_certificado.get("valido_hasta", "")[:10]
            item = QListWidgetItem(f"{perfil.nombre_mostrado}\nVigente hasta: {vigente_hasta}")
            item.setData(Qt.ItemDataRole.UserRole, perfil.id)
            self.lista.addItem(item)

    def _agregar_perfil(self):
        dialogo = DialogoNuevoPerfil(self.gestor_perfiles, self)
        if dialogo.exec():
            self.recargar()

    def _eliminar_seleccionado(self):
        item = self.lista.currentItem()
        if not item:
            return
        perfil_id = item.data(Qt.ItemDataRole.UserRole)
        confirmacion = QMessageBox.question(
            self, "Eliminar perfil",
            "¿Seguro que deseas eliminar este perfil? Esta acción no se puede deshacer."
        )
        if confirmacion == QMessageBox.StandardButton.Yes:
            self.gestor_perfiles.eliminar_perfil(perfil_id)
            self.recargar()
