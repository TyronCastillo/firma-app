"""Punto de entrada de la app de firma electrónica."""
import sys
from PyQt6.QtWidgets import QApplication

from ui.ventana_principal import VentanaPrincipal


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
