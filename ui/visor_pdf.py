"""
Widget que muestra la primera página de un PDF y permite al usuario
arrastrar un rectángulo para elegir dónde va la firma visualmente.
Usa PyMuPDF (fitz) para renderizar la página a imagen.
"""
import fitz  # PyMuPDF
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen, QColor
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal


class VisorPdfConSeleccion(QLabel):
    """
    Renderiza la página 0 de un PDF y permite arrastrar un rectángulo.
    Expone `rectangulo_pdf` con las coordenadas en el sistema de puntos
    del PDF (origen abajo-izquierda), listas para pasar a PosicionFirma.
    """
    seleccion_cambiada = pyqtSignal()

    ZOOM = 1.5  # factor de renderizado para que se vea nítido

    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background-color: #e5e7eb; border: 1px solid #cbd5e1;")
        self.setMouseTracking(True)

        self._documento = None
        self._pixmap_base = None
        self._alto_pagina_pdf = 0
        self._ancho_pagina_pdf = 0

        self._arrastrando = False
        self._inicio = QPoint()
        self._fin = QPoint()
        self.rectangulo_pdf = None  # (x0, y0, x1, y1) en puntos PDF

    def cargar_pdf(self, ruta_pdf: str):
        self._documento = fitz.open(ruta_pdf)
        pagina = self._documento[0]
        self._ancho_pagina_pdf = pagina.rect.width
        self._alto_pagina_pdf = pagina.rect.height

        matriz = fitz.Matrix(self.ZOOM, self.ZOOM)
        pix = pagina.get_pixmap(matrix=matriz)
        imagen = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
        self._pixmap_base = QPixmap.fromImage(imagen)
        self.setFixedSize(self._pixmap_base.size())
        self.rectangulo_pdf = None
        self._repintar()

    def _repintar(self):
        if self._pixmap_base is None:
            return
        lienzo = QPixmap(self._pixmap_base)
        pintor = QPainter(lienzo)
        if self._arrastrando or self.rectangulo_pdf:
            rect = QRect(self._inicio, self._fin).normalized() if self._arrastrando else self._rect_pdf_a_widget()
            pintor.setPen(QPen(QColor("#2563eb"), 2))
            pintor.setBrush(QColor(37, 99, 235, 60))
            pintor.drawRect(rect)
        pintor.end()
        self.setPixmap(lienzo)

    def _rect_pdf_a_widget(self) -> QRect:
        """Convierte rectangulo_pdf (coords PDF) de vuelta a coords de widget, para redibujar."""
        x0, y0, x1, y1 = self.rectangulo_pdf
        alto_img = self._pixmap_base.height()
        wx0 = x0 * self.ZOOM
        wx1 = x1 * self.ZOOM
        wy0 = alto_img - (y1 * self.ZOOM)
        wy1 = alto_img - (y0 * self.ZOOM)
        return QRect(QPoint(int(wx0), int(wy0)), QPoint(int(wx1), int(wy1)))

    def mousePressEvent(self, evento):
        if self._pixmap_base is None:
            return
        self._arrastrando = True
        self._inicio = evento.position().toPoint()
        self._fin = self._inicio

    def mouseMoveEvent(self, evento):
        if not self._arrastrando:
            return
        self._fin = evento.position().toPoint()
        self._repintar()

    def mouseReleaseEvent(self, evento):
        if not self._arrastrando:
            return
        self._arrastrando = False
        self._fin = evento.position().toPoint()

        rect_widget = QRect(self._inicio, self._fin).normalized()
        if rect_widget.width() < 10 or rect_widget.height() < 10:
            # selección demasiado pequeña, se ignora
            self._repintar()
            return

        # Convertir de coords de widget (Y hacia abajo) a coords PDF (Y hacia arriba)
        alto_img = self._pixmap_base.height()
        x0 = rect_widget.left() / self.ZOOM
        x1 = rect_widget.right() / self.ZOOM
        y0 = (alto_img - rect_widget.bottom()) / self.ZOOM
        y1 = (alto_img - rect_widget.top()) / self.ZOOM

        self.rectangulo_pdf = (x0, y0, x1, y1)
        self._repintar()
        self.seleccion_cambiada.emit()
