import math
import time

from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Signal, Property, QTimer
from PySide6.QtGui import QPainter

from card import ToolCard


class Carousel(QWidget):
    tool_changed = Signal(dict)

    CARD_W = ToolCard.CARD_W
    CARD_H = ToolCard.CARD_H
    REFL_H = ToolCard.REFL_H

    RADIUS      = 900
    ANGLE_STEP  = 44
    FOCAL       = 360
    MAX_VISIBLE = 4

    CARD_Y_OFFSET = 70    # push all cards down by this many pixels

    BOB_AMPLITUDE = 8     # pixels up/down
    BOB_SPEED     = 0.6   # cycles/sec — one full bob every ~5.5 seconds
    BOB_PHASE_GAP = 0.8   # phase offset between adjacent cards

    def __init__(self, tools, parent=None):
        super().__init__(parent)
        self.tools = tools
        self._pos  = 0.0
        self._idx  = 0
        self._anim = None
        self._t    = time.monotonic()

        self._cards = [ToolCard(t) for t in tools]
        self._face_cache: dict[int, QPixmap] = {}

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(self.CARD_H + 24 + self.REFL_H + 20 + self.CARD_Y_OFFSET)

        self._bob_timer = QTimer(self)
        self._bob_timer.setInterval(16)
        self._bob_timer.timeout.connect(self._tick)
        self._bob_timer.start()

    def _tick(self):
        # Snapshot time once — all cards share the same t this frame
        self._t = time.monotonic()
        self.update()

    def _get_pos(self): return self._pos
    def _set_pos(self, v):
        self._pos = v
        self.update()
    carousel_pos = Property(float, _get_pos, _set_pos)

    def _bob(self, i: int) -> float:
        phase = i * self.BOB_PHASE_GAP
        return math.sin(self._t * self.BOB_SPEED * 2 * math.pi + phase) * self.BOB_AMPLITUDE

    def _params(self, idx: int):
        diff  = idx - self._pos
        theta = math.radians(diff * self.ANGLE_STEP)

        x_3d = self.RADIUS * math.sin(theta)
        z    = self.FOCAL + self.RADIUS * (1.0 - math.cos(theta))

        scale     = self.FOCAL / z
        w         = self.width() or 880
        screen_cx = w // 2 + self.FOCAL * x_3d / z

        depth   = (z - self.FOCAL) / self.RADIUS
        opacity = max(0.0, 1.0 - depth * 0.52)

        ch     = int(self.CARD_H * scale)
        card_y = self.CARD_H - ch + self.CARD_Y_OFFSET   # bottom-align + push down

        return screen_cx, card_y, scale, opacity, z

    def _face(self, idx: int):
        if idx not in self._face_cache:
            self._face_cache[idx] = self._cards[idx]._render_card_face()
        return self._face_cache[idx]

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        entries = []
        for i in range(len(self._cards)):
            diff = i - self._pos
            if abs(diff) > self.MAX_VISIBLE + 0.5:
                continue
            if abs(diff) * self.ANGLE_STEP >= 179:
                continue
            cx, cy, scale, opacity, z = self._params(i)
            if opacity > 0.02:
                bob  = self._bob(i)
                face = self._face(i)   # cached — rendered once, reused for both card and reflection
                entries.append((z, i, self._cards[i], cx, cy, scale, opacity, bob, face))

        entries.sort(key=lambda e: -e[0])

        # Pass 1 — reflections (bob negated so reflection moves opposite to card)
        for z, i, card, cx, cy, scale, opacity, bob, face in entries:
            cw = int(self.CARD_W * scale)
            x0 = int(cx) - cw // 2
            card._scale   = scale
            card._opacity = opacity
            card.render_reflection(p, x0, int(cy - bob), face)

        # Pass 2 — card faces
        for z, i, card, cx, cy, scale, opacity, bob, face in entries:
            cw = int(self.CARD_W * scale)
            ch = int(self.CARD_H * scale)
            x0 = int(cx) - cw // 2
            p.setOpacity(opacity)
            p.drawPixmap(x0, int(cy + bob), cw, ch, face)

        p.setOpacity(1.0)
        p.end()

    def _go(self, delta: int):
        new = max(0, min(len(self._cards) - 1, self._idx + delta))
        if new == self._idx:
            return
        self._idx = new
        if self._anim:
            self._anim.stop()
        self._anim = QPropertyAnimation(self, b"carousel_pos")
        self._anim.setDuration(380)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.setStartValue(self._pos)
        self._anim.setEndValue(float(new))
        self._anim.start()
        self.tool_changed.emit(self.tools[self._idx])

    def go_next(self): self._go(+1)
    def go_prev(self): self._go(-1)

    def resizeEvent(self, event): self.update()
    def showEvent(self, event):
        super().showEvent(event)
        self.update()