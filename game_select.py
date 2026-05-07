import re
from pathlib import Path

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QRectF, QRect, Signal, Property
from PySide6.QtGui import (
    QColor, QPixmap, QPainter, QLinearGradient, QRadialGradient,
    QPen, QFont, QPainterPath
)

from background import Background
from paths import ASSET_ROOT
from updater import APP_VERSION, fmt_version, start_check, start_apply

GAME_ICON_DIR = ASSET_ROOT / "assets" / "game_icons"


def _generate_game_banner(game: dict, w: int, h: int) -> QPixmap:
    pix = QPixmap(w, h)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)

    accent: QColor = game["accent"]

    bg = QLinearGradient(0, 0, w, h)
    bg.setColorAt(0.0, QColor(8, 10, 16))
    bg.setColorAt(1.0, QColor(15, 18, 28))
    p.fillRect(0, 0, w, h, bg)

    glow = QRadialGradient(w * 0.5, h * 0.35, w * 0.9)
    c = QColor(accent); c.setAlpha(55)
    glow.setColorAt(0.0, c)
    glow.setColorAt(1.0, Qt.transparent)
    p.fillRect(0, 0, w, h, glow)

    pen = QPen(QColor(255, 255, 255, 8)); pen.setWidth(1)
    p.setPen(pen)
    for x in range(0, w, 30):
        p.drawLine(x, 0, x, h)
    for y in range(0, h, 30):
        p.drawLine(0, y, w, y)

    p.setPen(QPen(QColor(accent.red(), accent.green(), accent.blue(), 50), 1))
    p.setFont(QFont("Segoe UI Symbol", 130))
    p.drawText(QRect(w // 2 - 130, h // 2 - 150, 260, 260), Qt.AlignCenter, game["icon_char"])

    sl = QLinearGradient(0, h - 3, w, h - 3)
    sl.setColorAt(0.0, Qt.transparent)
    sl.setColorAt(0.4, accent)
    sl.setColorAt(0.6, accent)
    sl.setColorAt(1.0, Qt.transparent)
    p.fillRect(0, h - 3, w, 3, sl)

    p.end()
    return pix


class GameCard(QWidget):
    clicked = Signal(dict)
    hovered = Signal(dict)
    left    = Signal()

    W = 360
    H = 440

    def __init__(self, game: dict, parent=None):
        super().__init__(parent)
        self.game = game
        self.setFixedSize(self.W, self.H)
        self._hovered = False
        self.banner   = _generate_game_banner(game, self.W, self.H)
        self._icon_px = self._load_icon(game)
        self.setCursor(Qt.PointingHandCursor)

    @staticmethod
    def _load_icon(game: dict) -> QPixmap | None:
        slug = re.sub(r'[^a-z0-9]+', '_', game["short"].lower()).strip('_')
        path = GAME_ICON_DIR / f"{slug}.png"
        if path.exists():
            pm = QPixmap(str(path))
            return pm if not pm.isNull() else None
        return None

    def enterEvent(self, event):
        self._hovered = True
        self.hovered.emit(self.game)
        self.update()

    def leaveEvent(self, event):
        self._hovered = False
        self.left.emit()
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.game)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        accent: QColor = self.game["accent"]
        w, h = self.W, self.H

        if self._icon_px:
            # ── Icon mode — PNG centred, transparent background ──────────────
            pad = 30
            scaled = self._icon_px.scaled(
                w - pad * 2, h - pad * 2,
                Qt.KeepAspectRatio, Qt.SmoothTransformation,
            )
            ix = (w - scaled.width()) // 2
            iy = (h - scaled.height()) // 2
            p.setOpacity(0.75 if not self._hovered else 1.0)
            p.drawPixmap(ix, iy, scaled)
            p.setOpacity(1.0)

            # Subtle accent glow on hover
            if self._hovered:
                glow = QRadialGradient(w / 2, h / 2, w * 0.7)
                gc = QColor(accent); gc.setAlpha(30)
                glow.setColorAt(0, gc); gc.setAlpha(0); glow.setColorAt(1, gc)
                p.fillRect(0, 0, w, h, glow)

            border_alpha = 160 if self._hovered else 70
            p.setPen(QPen(QColor(accent.red(), accent.green(), accent.blue(), border_alpha), 1.5))
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(QRectF(0.75, 0.75, w - 1.5, h - 1.5), 14, 14)

            tool_count = len(self.game["tools"])
            count_text = f"{tool_count} TOOL{'S' if tool_count != 1 else ''}" if tool_count else "COMING SOON"
            count_rect = QRectF(16, h - 114, w - 32, 22)
            p.setBrush(QColor(255, 255, 255, 10)); p.setPen(Qt.NoPen)
            p.drawRoundedRect(count_rect, 4, 4)
            p.setPen(QColor(accent.red(), accent.green(), accent.blue(), 180))
            p.setFont(QFont("Consolas", 9, QFont.Bold))
            p.drawText(count_rect, Qt.AlignCenter, count_text)
        else:
            # ── Procedural fallback ──────────────────────────────────────────
            path = QPainterPath()
            path.addRoundedRect(QRectF(0, 0, w, h), 14, 14)
            p.setClipPath(path)
            p.drawPixmap(0, 0, self.banner)
            p.setClipping(False)

            if self._hovered:
                overlay = QColor(accent); overlay.setAlpha(18)
                p.fillRect(0, 0, w, h, overlay)

            border_alpha = 160 if self._hovered else 70
            p.setPen(QPen(QColor(accent.red(), accent.green(), accent.blue(), border_alpha), 1.5))
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(QRectF(0.75, 0.75, w - 1.5, h - 1.5), 14, 14)

            tag_rect = QRectF(16, 16, w - 32, 26)
            tag_bg = QColor(accent); tag_bg.setAlpha(180)
            p.setBrush(tag_bg); p.setPen(Qt.NoPen)
            p.drawRoundedRect(tag_rect, 4, 4)
            p.setPen(QColor(0, 0, 0, 220))
            p.setFont(QFont("Consolas", 9, QFont.Bold))
            p.drawText(tag_rect, Qt.AlignCenter, self.game["tag"])

            tool_count = len(self.game["tools"])
            count_text = f"{tool_count} TOOL{'S' if tool_count != 1 else ''}" if tool_count else "COMING SOON"
            count_rect = QRectF(16, h - 114, w - 32, 22)
            p.setBrush(QColor(255, 255, 255, 10)); p.setPen(Qt.NoPen)
            p.drawRoundedRect(count_rect, 4, 4)
            p.setPen(QColor(accent.red(), accent.green(), accent.blue(), 180))
            p.setFont(QFont("Consolas", 9, QFont.Bold))
            p.drawText(count_rect, Qt.AlignCenter, count_text)

            p.setPen(QColor(255, 255, 255, 240))
            p.setFont(QFont("Segoe UI", 15, QFont.Bold))
            p.drawText(QRectF(18, h - 94, w - 36, 54), Qt.AlignLeft | Qt.AlignVCenter | Qt.TextWordWrap, self.game["name"])

            p.setPen(QColor(180, 200, 230, 150))
            p.setFont(QFont("Segoe UI", 10))
            p.drawText(QRectF(18, h - 44, w - 36, 38), Qt.AlignLeft | Qt.AlignTop | Qt.TextWordWrap, self.game["desc"])

        p.end()


class GameSelectScreen(QWidget):
    game_selected = Signal(dict)

    def __init__(self, games: list, parent=None):
        super().__init__(parent)

        self.bg = Background(self)
        self.bg.setGeometry(self.rect())
        self.bg.set_accent(QColor(255, 255, 255))

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Center
        center = QVBoxLayout()
        center.setContentsMargins(0, 0, 0, 0)
        center.setSpacing(0)

        # Header
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet("background: transparent;")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(30, 0, 30, 0)

        # Version label (far left)
        ver_lbl = QLabel(fmt_version(APP_VERSION))
        ver_lbl.setStyleSheet(
            "font-family: Consolas; font-size: 12px; letter-spacing: 1px; color: rgba(255,255,255,255);"
        )
        h_layout.addWidget(ver_lbl)

        # Update button — hidden until a newer version is found
        self._update_btn = QPushButton("")
        self._update_btn.setFixedHeight(22)
        self._update_btn.setVisible(False)
        self._update_btn.setStyleSheet("""
            QPushButton {
                font-family: Consolas; font-size: 9px; font-weight: bold;
                letter-spacing: 1px; border: 1px solid rgba(80,220,120,60);
                border-radius: 3px; background: rgba(80,220,120,10);
                color: rgba(80,220,120,200); padding: 0 10px;
            }
            QPushButton:hover {
                background: rgba(80,220,120,22); color: rgba(110,255,150,255);
                border-color: rgba(80,220,120,120);
            }
            QPushButton:disabled {
                color: rgba(255,255,255,30); border-color: rgba(255,255,255,15);
                background: rgba(255,255,255,5);
            }
        """)
        self._update_btn.clicked.connect(self._do_update)
        h_layout.addWidget(self._update_btn)

        h_layout.addStretch()

        count_lbl = QLabel(f"{len(games)} GAMES")
        count_lbl.setStyleSheet("""
            font-family: Consolas; font-size: 12px;
            letter-spacing: 2px; color: rgba(255,255,255,255);
        """)
        h_layout.addWidget(count_lbl)
        center.addWidget(header)

        center.addStretch()

        # Game cards row
        cards_row = QHBoxLayout()
        cards_row.setSpacing(40)
        cards_row.addStretch()

        for game in games:
            card = GameCard(game)
            card.clicked.connect(self.game_selected.emit)
            card.hovered.connect(lambda g: self.bg.set_accent(g["accent"]))
            card.left.connect(lambda: self.bg.set_accent(QColor(255, 255, 255)))
            cards_row.addWidget(card)

        cards_row.addStretch()
        center.addLayout(cards_row)

        center.addStretch()
        root.addLayout(center, 1)

        # Start background version check silently
        self._check_thread = start_check(self._on_check_result)
        self._apply_thread = None

    # ── Update slots ───────────────────────────────────────────────────────────

    def _on_check_result(self, status: str, remote_ver):
        if status == "update_available":
            self._update_btn.setText(f"↓  UPDATE  {fmt_version(remote_ver)}")
            self._update_btn.setVisible(True)

    def _do_update(self):
        self._update_btn.setText("↓  UPDATING...")
        self._update_btn.setEnabled(False)
        self._apply_thread = start_apply(self._on_apply_progress, self._on_apply_done, parent=self)

    def _on_apply_progress(self, done: int, total: int):
        self._update_btn.setText(f"↓  UPDATING  {done}/{total}")

    def _on_apply_done(self, failed):
        if failed:
            self._update_btn.setText("✕  UPDATE FAILED")
            self._update_btn.setEnabled(True)
            for msg in failed:
                print(f"[updater] FAILED: {msg}")
        else:
            self._update_btn.setText("✓  RESTART TO APPLY")

    def resizeEvent(self, event):
        self.bg.setGeometry(self.rect())
        super().resizeEvent(event)