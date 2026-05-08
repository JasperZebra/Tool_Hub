from pathlib import Path

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRect, QRectF, Property
from PySide6.QtGui import (
    QColor, QPixmap, QPainter, QLinearGradient, QRadialGradient,
    QTransform, QFont, QPen, QPainterPath, QConicalGradient
)

from paths import ASSET_ROOT

ICON_DIR = ASSET_ROOT / "assets" / "tool_icons"


def generate_card_image(tool: dict, w: int, h: int) -> QPixmap:
    pix = QPixmap(w, h)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)

    accent: QColor = tool["accent"]

    bg = QLinearGradient(0, 0, w, h)
    bg.setColorAt(0.0, QColor(8, 10, 16))
    bg.setColorAt(1.0, QColor(15, 18, 28))
    p.fillRect(0, 0, w, h, bg)

    glow = QRadialGradient(w * 0.75, h * 0.2, w * 0.7)
    c = QColor(accent)
    c.setAlpha(55)
    glow.setColorAt(0.0, c)
    glow.setColorAt(1.0, Qt.transparent)
    p.fillRect(0, 0, w, h, glow)

    pen = QPen(QColor(255, 255, 255, 10))
    pen.setWidth(1)
    p.setPen(pen)
    for x in range(0, w, 30):
        p.drawLine(x, 0, x, h)
    for y in range(0, h, 30):
        p.drawLine(0, y, w, y)

    icon = tool["icon_char"]
    p.setPen(QPen(QColor(accent.red(), accent.green(), accent.blue(), 80), 1))
    font = QFont("Segoe UI Symbol", 140)
    p.setFont(font)
    p.drawText(QRect(w // 2 - 140, h // 2 - 120, 280, 240), Qt.AlignCenter, icon)

    sl = QLinearGradient(0, h - 3, w, h - 3)
    sl.setColorAt(0.0, Qt.transparent)
    sl.setColorAt(0.4, accent)
    sl.setColorAt(0.6, accent)
    sl.setColorAt(1.0, Qt.transparent)
    p.fillRect(0, h - 3, w, 3, sl)

    p.end()
    return pix


class ToolCard(QWidget):
    CARD_W = 520
    CARD_H = 340
    REFL_H = 210

    def __init__(self, tool: dict, parent=None):
        super().__init__(parent)
        self.tool = tool
        self.setFixedSize(self.CARD_W, self.CARD_H + 24 + self.REFL_H + 8)
        self._scale   = 1.0
        self._opacity = 1.0

        self.banner   = generate_card_image(tool, self.CARD_W, self.CARD_H)
        self._icon_px = self._load_icon(tool)

    @staticmethod
    def _load_icon(tool: dict) -> QPixmap | None:
        folder = tool.get("folder")
        if not folder:
            return None
        path = ICON_DIR / f"{folder.name}.png"
        if path.exists():
            pm = QPixmap(str(path))
            return pm if not pm.isNull() else None
        return None

    def get_scale(self): return self._scale
    def set_scale(self, v):
        self._scale = v
        self.update()
    card_scale = Property(float, get_scale, set_scale)

    def get_opacity(self): return self._opacity
    def set_opacity(self, v):
        self._opacity = v
        self.update()
    card_opacity = Property(float, get_opacity, set_opacity)

    def _render_card_face(self) -> QPixmap:
        cw, ch = self.CARD_W, self.CARD_H
        pix = QPixmap(cw, ch)
        pix.fill(Qt.transparent)
        p = QPainter(pix)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        accent: QColor = self.tool["accent"]

        clip = QPainterPath()
        clip.addRoundedRect(QRectF(0, 0, cw, ch), 12, 12)
        p.setClipPath(clip)

        if self._icon_px:
            pass
        else:
            p.drawPixmap(0, 0, cw, ch, self.banner)

        if self._icon_px:
            pad = 40
            scaled = self._icon_px.scaled(
                cw - pad * 2, ch - pad * 2,
                Qt.KeepAspectRatio, Qt.SmoothTransformation,
            )
            ix = (cw - scaled.width()) // 2
            iy = (ch - scaled.height()) // 2
            p.drawPixmap(ix, iy, scaled)
        else:
            game_accent: QColor = self.tool.get("game_accent", accent)
            tag_rect = QRectF(16, 16, cw - 32, 30)
            tag_bg = QColor(game_accent); tag_bg.setAlpha(200)
            p.setBrush(tag_bg); p.setPen(Qt.NoPen)
            p.drawRoundedRect(tag_rect, 4, 4)
            p.setPen(QColor(0, 0, 0, 220))
            p.setFont(QFont("Consolas", 12, QFont.Bold))
            p.drawText(tag_rect, Qt.AlignCenter, self.tool["tag"])

            p.setPen(QColor(255, 255, 255, 240))
            p.setFont(QFont("Segoe UI", 22, QFont.Bold))
            p.drawText(QRectF(18, ch - 120, cw - 36, 40), Qt.AlignLeft | Qt.AlignVCenter, self.tool["name"])

            p.setPen(QColor(200, 210, 230, 180))
            p.setFont(QFont("Segoe UI", 11))
            p.drawText(QRectF(18, ch - 80, cw - 36, 76), Qt.AlignLeft | Qt.AlignTop | Qt.TextWordWrap, self.tool["desc"])

        p.setClipping(False)

        if not self._icon_px:
            p.setPen(QPen(QColor(accent.red(), accent.green(), accent.blue(), 120), 1.5))
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(QRectF(0.75, 0.75, cw - 1.5, ch - 1.5), 12, 12)

            bar_line = QLinearGradient(0, ch - 0.5, cw, ch - 0.5)
            bar_line.setColorAt(0, Qt.transparent)
            bar_line.setColorAt(0.5, accent)
            bar_line.setColorAt(1, Qt.transparent)
            p.setPen(Qt.NoPen); p.setBrush(bar_line)
            p.drawRect(QRectF(0, ch - 1, cw, 1))

        p.end()
        return pix

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        p.setOpacity(self._opacity)
        cw = int(self.CARD_W * self._scale)
        ch = int(self.CARD_H * self._scale)
        x0 = self.width() // 2 - cw // 2
        p.drawPixmap(x0, 0, cw, ch, self._render_card_face())
        p.end()

    def render_reflection(self, painter: QPainter, x0: int, y0: int, face: QPixmap):
        """Draw reflection using a pre-rendered face pixmap — no re-render."""
        cw = int(self.CARD_W * self._scale)
        ch = int(self.CARD_H * self._scale)
        rh = int(ch * 0.60)
        if rh <= 0:
            return

        flipped = face.transformed(QTransform().scale(1, -1))
        gap = 24
        refl_y = y0 + ch + gap

        refl_pix = QPixmap(cw, rh)
        refl_pix.fill(Qt.transparent)

        src_h = int(self.CARD_H * rh / ch)

        rp = QPainter(refl_pix)
        rp.setRenderHint(QPainter.SmoothPixmapTransform)
        rp.drawPixmap(0, 0, cw, rh, flipped, 0, 0, self.CARD_W, src_h)

        rp.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        mask = QLinearGradient(0, 0, 0, rh)
        mask.setColorAt(0.0, QColor(0, 0, 0, 50))
        mask.setColorAt(0.5, QColor(0, 0, 0, 12))
        mask.setColorAt(1.0, QColor(0, 0, 0, 0))
        rp.fillRect(0, 0, cw, rh, mask)
        rp.end()

        blurred = refl_pix.scaled(
            max(1, cw // 2), max(1, rh // 2),
            Qt.IgnoreAspectRatio, Qt.SmoothTransformation
        )

        painter.setOpacity(self._opacity)
        painter.drawPixmap(x0, refl_y, cw, rh, blurred)
        painter.setOpacity(1.0)