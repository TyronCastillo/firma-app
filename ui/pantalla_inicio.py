"""Pantalla de inicio: los dos accesos principales, igual que Firmatic."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, pyqtSignal


class PantallaInicio(QWidget):
    ir_a_firmar = pyqtSignal()
    ir_a_perfiles = pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 80, 60, 80)
        layout.setSpacing(24)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        titulo = QLabel("Firma Electrónica")
        titulo.setStyleSheet("font-size: 26px; font-weight: 600;")
        layout.addWidget(titulo)

        subtitulo = QLabel("Firma tus documentos PDF de forma local y segura")
        subtitulo.setStyleSheet("font-size: 14px; color: #666;")
        layout.addWidget(subtitulo)

        layout.addSpacing(30)

        boton_firmar = QPushButton("📄  Firmar PDF")
        boton_firmar.setMinimumHeight(56)
        boton_firmar.setStyleSheet(self._estilo_boton_principal())
        boton_firmar.clicked.connect(self.ir_a_firmar.emit)
        layout.addWidget(boton_firmar)

        boton_perfiles = QPushButton("👤  Perfiles")
        boton_perfiles.setMinimumHeight(56)
        boton_perfiles.setStyleSheet(self._estilo_boton_secundario())
        boton_perfiles.clicked.connect(self.ir_a_perfiles.emit)
        layout.addWidget(boton_perfiles)

    @staticmethod
    def _estilo_boton_principal():
        return """
            QPushButton {
                background-color: #2563eb; color: white; font-size: 16px;
                border-radius: 10px; font-weight: 500;
            }
            QPushButton:hover { background-color: #1d4ed8; }
        """

    @staticmethod
    def _estilo_boton_secundario():
        return """
            QPushButton {
                background-color: #f1f5f9; color: #1e293b; font-size: 16px;
                border-radius: 10px; font-weight: 500; border: 1px solid #cbd5e1;
            }
            QPushButton:hover { background-color: #e2e8f0; }
        """
