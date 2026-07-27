"""Pantalla principal de firma: seleccionar PDF -> posicionar -> elegir perfil -> firmar."""
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QLineEdit, QFileDialog, QMessageBox, QScrollArea
)
from PyQt6.QtCore import pyqtSignal

from core.perfiles import GestorPerfiles
from core.firmador import firmar_pdf, PosicionFirma, ErrorFirma
from core.certificado import CertificadoInvalidoError
from .visor_pdf import VisorPdfConSeleccion


class PantallaFirmar(QWidget):
    volver = pyqtSignal()

    def __init__(self, gestor_perfiles: GestorPerfiles):
        super().__init__()
        self.gestor_perfiles = gestor_perfiles
        self._ruta_pdf = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)

        cabecera = QHBoxLayout()
        boton_volver = QPushButton("←")
        boton_volver.setFixedWidth(36)
        boton_volver.clicked.connect(self.volver.emit)
        titulo = QLabel("Firmar PDF")
        titulo.setStyleSheet("font-size: 20px; font-weight: 600;")
        cabecera.addWidget(boton_volver)
        cabecera.addWidget(titulo)
        cabecera.addStretch()
        layout.addLayout(cabecera)

        self.boton_elegir_pdf = QPushButton("📁  Seleccionar PDF a firmar")
        self.boton_elegir_pdf.clicked.connect(self._elegir_pdf)
        layout.addWidget(self.boton_elegir_pdf)

        self.etiqueta_ayuda = QLabel("Selecciona un PDF y luego arrastra un recuadro donde quieras la firma.")
        self.etiqueta_ayuda.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(self.etiqueta_ayuda)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.visor = VisorPdfConSeleccion()
        scroll.setWidget(self.visor)
        layout.addWidget(scroll, stretch=1)

        fila_perfil = QHBoxLayout()
        fila_perfil.addWidget(QLabel("Perfil:"))
        self.combo_perfiles = QComboBox()
        fila_perfil.addWidget(self.combo_perfiles, stretch=1)
        layout.addLayout(fila_perfil)

        fila_clave = QHBoxLayout()
        fila_clave.addWidget(QLabel("Contraseña:"))
        self.campo_contrasena = QLineEdit()
        self.campo_contrasena.setEchoMode(QLineEdit.EchoMode.Password)
        fila_clave.addWidget(self.campo_contrasena, stretch=1)
        layout.addLayout(fila_clave)

        self.etiqueta_estado = QLabel("")
        self.etiqueta_estado.setWordWrap(True)
        layout.addWidget(self.etiqueta_estado)

        self.boton_firmar = QPushButton("✍️  Firmar documento")
        self.boton_firmar.setMinimumHeight(48)
        self.boton_firmar.setStyleSheet(
            "background-color: #2563eb; color: white; font-size: 15px; border-radius: 8px;"
        )
        self.boton_firmar.clicked.connect(self._firmar)
        layout.addWidget(self.boton_firmar)

    def mostrar(self):
        """Se llama cada vez que se navega a esta pantalla, para refrescar los perfiles."""
        self.combo_perfiles.clear()
        for perfil in self.gestor_perfiles.listar_perfiles():
            self.combo_perfiles.addItem(perfil.nombre_mostrado, perfil.id)
        if self.combo_perfiles.count() == 0:
            self.etiqueta_estado.setText("No tienes perfiles creados. Ve a 'Perfiles' para agregar uno.")

    def _elegir_pdf(self):
        ruta, _ = QFileDialog.getOpenFileName(self, "Selecciona el PDF a firmar", "", "PDF (*.pdf)")
        if ruta:
            self._ruta_pdf = ruta
            self.visor.cargar_pdf(ruta)
            self.boton_elegir_pdf.setText(f"📁  {Path(ruta).name}")

    def _firmar(self):
        self.etiqueta_estado.setText("")

        if not self._ruta_pdf:
            self.etiqueta_estado.setText("Primero selecciona un PDF.")
            return
        if self.combo_perfiles.count() == 0:
            self.etiqueta_estado.setText("Crea un perfil primero en la sección 'Perfiles'.")
            return
        if not self.visor.rectangulo_pdf:
            self.etiqueta_estado.setText("Arrastra un recuadro sobre el PDF para indicar dónde va la firma.")
            return
        if not self.campo_contrasena.text():
            self.etiqueta_estado.setText("Ingresa la contraseña del certificado.")
            return

        perfil_id = self.combo_perfiles.currentData()
        perfil = self.gestor_perfiles.obtener_perfil(perfil_id)

        ruta_salida, _ = QFileDialog.getSaveFileName(
            self, "Guardar PDF firmado",
            str(Path(self._ruta_pdf).with_name(Path(self._ruta_pdf).stem + "_firmado.pdf")),
            "PDF (*.pdf)"
        )
        if not ruta_salida:
            return

        x0, y0, x1, y1 = self.visor.rectangulo_pdf
        posicion = PosicionFirma(pagina=0, x0=x0, y0=y0, x1=x1, y1=y1)

        try:
            firmar_pdf(
                ruta_pdf_entrada=self._ruta_pdf,
                ruta_pdf_salida=ruta_salida,
                ruta_p12=perfil.ruta_p12,
                contrasena_p12=self.campo_contrasena.text(),
                posicion=posicion,
            )
            self.campo_contrasena.clear()
            QMessageBox.information(self, "Listo", f"Documento firmado guardado en:\n{ruta_salida}")
            self.etiqueta_estado.setText("✅ Firmado correctamente.")
        except CertificadoInvalidoError as e:
            self.etiqueta_estado.setText(f"❌ {e}")
        except ErrorFirma as e:
            self.etiqueta_estado.setText(f"❌ {e}")
