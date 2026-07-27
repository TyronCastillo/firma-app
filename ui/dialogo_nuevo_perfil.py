"""Diálogo modal para crear un perfil nuevo a partir de un .p12."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QFileDialog, QLabel, QHBoxLayout, QMessageBox
)

from core.perfiles import GestorPerfiles
from core.certificado import CertificadoInvalidoError


class DialogoNuevoPerfil(QDialog):
    def __init__(self, gestor_perfiles: GestorPerfiles, parent=None):
        super().__init__(parent)
        self.gestor_perfiles = gestor_perfiles
        self.perfil_creado = None

        self.setWindowTitle("Nuevo perfil")
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)

        # Selector de archivo .p12
        fila_archivo = QHBoxLayout()
        self.campo_ruta = QLineEdit()
        self.campo_ruta.setReadOnly(True)
        self.campo_ruta.setPlaceholderText("Selecciona tu archivo .p12...")
        boton_examinar = QPushButton("Examinar...")
        boton_examinar.clicked.connect(self._elegir_archivo)
        fila_archivo.addWidget(self.campo_ruta)
        fila_archivo.addWidget(boton_examinar)
        layout.addLayout(fila_archivo)

        # Formulario
        formulario = QFormLayout()
        self.campo_contrasena = QLineEdit()
        self.campo_contrasena.setEchoMode(QLineEdit.EchoMode.Password)
        formulario.addRow("Contraseña del certificado:", self.campo_contrasena)

        self.campo_nombre = QLineEdit()
        self.campo_nombre.setPlaceholderText("(opcional, se toma del certificado)")
        formulario.addRow("Nombre del perfil:", self.campo_nombre)
        layout.addLayout(formulario)

        self.etiqueta_error = QLabel("")
        self.etiqueta_error.setStyleSheet("color: #dc2626;")
        self.etiqueta_error.setWordWrap(True)
        layout.addWidget(self.etiqueta_error)

        # Botones
        fila_botones = QHBoxLayout()
        boton_cancelar = QPushButton("Cancelar")
        boton_cancelar.clicked.connect(self.reject)
        boton_guardar = QPushButton("Guardar perfil")
        boton_guardar.setStyleSheet("background-color: #2563eb; color: white; padding: 6px 16px; border-radius: 6px;")
        boton_guardar.clicked.connect(self._guardar)
        fila_botones.addStretch()
        fila_botones.addWidget(boton_cancelar)
        fila_botones.addWidget(boton_guardar)
        layout.addLayout(fila_botones)

        self._ruta_seleccionada = None

    def _elegir_archivo(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Selecciona tu certificado", "", "Certificados PKCS#12 (*.p12 *.pfx)"
        )
        if ruta:
            self._ruta_seleccionada = ruta
            self.campo_ruta.setText(ruta)

    def _guardar(self):
        self.etiqueta_error.setText("")

        if not self._ruta_seleccionada:
            self.etiqueta_error.setText("Debes seleccionar un archivo .p12")
            return
        if not self.campo_contrasena.text():
            self.etiqueta_error.setText("Debes ingresar la contraseña del certificado")
            return

        try:
            self.perfil_creado = self.gestor_perfiles.crear_perfil(
                ruta_p12_original=self._ruta_seleccionada,
                contrasena=self.campo_contrasena.text(),
                nombre_mostrado=self.campo_nombre.text() or None,
            )
            self.accept()
        except CertificadoInvalidoError as e:
            self.etiqueta_error.setText(str(e))
        except Exception as e:
            self.etiqueta_error.setText(f"Error inesperado: {e}")
