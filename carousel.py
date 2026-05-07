import math

from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Signal, Property
from PySide6.QtGui import QPainter

from card import ToolCard


class Carousel(QWidget):
    tool_changed = Signal(dict)

    CARD_W = ToolCard.CARD_W
    CARD_H = ToolCard.CARD_H
    REFL_H = ToolCard.REFL_H

    RADIUS      = 900   # bigger = more depth between center and background
    ANGLE_STEP  = 44    # 4 × 44 = 176° — stays under 180° so order never flips
    FOCAL       = 360   # smaller = more dramatic size difference front-to-back
    MAX_VISIBLE = 4     # cards shown per side (so you see them receding)

    def __init__(self, tools, parent=None):
        super().__init__(parent)
        self.tools = tools
        self._pos  = 0.0
        self._idx  = 0
        self._anim = None

        self._cards = [ToolCard(t) for t in tools]
        self._face_cache: dict[int, object] = {}

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(self.CARD_H + 24 + self.REFL_H + 20)

    # ── Animatable Qt property ────────────────────────────────────────────────

    def _get_pos(self): return self._pos
    def _set_pos(self, v):
        self._pos = v
        self.update()
    carousel_pos = Property(float, _get_pos, _set_pos)

    # ── 3-D perspective math ──────────────────────────────────────────────────

    def _params(self, idx: int):
        """Return (screen_cx, card_y, scale, opacity, z) for card idx."""
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
        card_y = self.CARD_H - ch          # bottom-align all cards

        return screen_cx, card_y, scale, opacity, z

    def _face(self, idx: int):
        if idx not in self._face_cache:
            self._face_cache[idx] = self._cards[idx]._render_card_face()
        return self._face_cache[idx]

    # ── Painting ──────────────────────────────────────────────────────────────

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        entries = []
        for i in range(len(self._cards)):
            diff = i - self._pos
            if abs(diff) > self.MAX_VISIBLE + 0.5:
                continue
            if abs(diff) * self.ANGLE_STEP >= 179:   # never let a card cross 180°
                continue
            cx, cy, scale, opacity, z = self._params(i)
            if opacity > 0.02:
                entries.append((z, i, self._cards[i], cx, cy, scale, opacity))

        entries.sort(key=lambda e: -e[0])   # back → front

        # Pass 1 — reflections
        for z, i, card, cx, cy, scale, opacity in entries:
            cw = int(self.CARD_W * scale)
            x0 = int(cx) - cw // 2
            card._scale   = scale
            card._opacity = opacity
            card.render_reflection(p, x0, cy)

        # Pass 2 — card faces
        for z, i, card, cx, cy, scale, opacity in entries:
            cw = int(self.CARD_W * scale)
            ch = int(self.CARD_H * scale)
            x0 = int(cx) - cw // 2
            p.setOpacity(opacity)
            p.drawPixmap(x0, cy, cw, ch, self._face(i))

        p.setOpacity(1.0)
        p.end()

    # ── Navigation ────────────────────────────────────────────────────────────

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
