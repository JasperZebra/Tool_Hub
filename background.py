import math
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor, QPainter, QRadialGradient, QLinearGradient, QPen


class Background(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._accent = QColor(0, 180, 255)
        self._tick = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_tick)
        self._timer.start(50)

    def set_accent(self, color: QColor):
        self._accent = color
        self.update()

    def _on_tick(self):
        self._tick += 1
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # Base fill
        p.fillRect(0, 0, w, h, QColor(8, 10, 16))

        # Animated radial glow from center-bottom
        t = self._tick * 0.04
        pulse = 0.55 + 0.15 * math.sin(t)
        glow = QRadialGradient(w * 0.5, h * 0.85, h * pulse * 1.4)
        c = QColor(self._accent)
        c.setAlpha(30)
        glow.setColorAt(0, c)
        glow.setColorAt(1, QColor(0, 0, 0, 0))
        p.fillRect(0, 0, w, h, glow)

        # Scanlines
        p.setPen(QPen(QColor(255, 255, 255, 4), 1))
        for y in range(0, h, 3):
            p.drawLine(0, y, w, y)

        # Top edge accent line
        top_grad = QLinearGradient(0, 0, w, 0)
        top_grad.setColorAt(0, QColor(0, 0, 0, 0))
        top_grad.setColorAt(0.5, QColor(self._accent.red(), self._accent.green(), self._accent.blue(), 80))
        top_grad.setColorAt(1, QColor(0, 0, 0, 0))
        p.fillRect(0, 0, w, 1, top_grad)

        p.end()
