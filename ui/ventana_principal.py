"""Ventana principal: navega entre Inicio, Perfiles y Firmar, como la app Firmatic."""
from pathlib import Path

from PyQt6.QtWidgets import QMainWindow, QStackedWidget

from core.perfiles import GestorPerfiles
from .pantalla_inicio import PantallaInicio
from .pantalla_perfiles import PantallaPerfiles
from .pantalla_firmar import PantallaFirmar


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Firma Electrónica")
        self.resize(820, 780)

        directorio_datos = Path.home() / ".firma-app-datos"
        self.gestor_perfiles = GestorPerfiles(directorio_datos)

        self.pila = QStackedWidget()
        self.setCentralWidget(self.pila)

        self.pantalla_inicio = PantallaInicio()
        self.pantalla_perfiles = PantallaPerfiles(self.gestor_perfiles)
        self.pantalla_firmar = PantallaFirmar(self.gestor_perfiles)

        self.pila.addWidget(self.pantalla_inicio)
        self.pila.addWidget(self.pantalla_perfiles)
        self.pila.addWidget(self.pantalla_firmar)

        self.pantalla_inicio.ir_a_firmar.connect(self._ir_a_firmar)
        self.pantalla_inicio.ir_a_perfiles.connect(lambda: self.pila.setCurrentWidget(self.pantalla_perfiles))
        self.pantalla_perfiles.volver.connect(lambda: self.pila.setCurrentWidget(self.pantalla_inicio))
        self.pantalla_firmar.volver.connect(lambda: self.pila.setCurrentWidget(self.pantalla_inicio))

        self.pila.setCurrentWidget(self.pantalla_inicio)

    def _ir_a_firmar(self):
        self.pantalla_firmar.mostrar()
        self.pila.setCurrentWidget(self.pantalla_firmar)
