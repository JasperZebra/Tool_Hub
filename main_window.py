import re
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QGridLayout, QStackedWidget, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QShortcut, QKeySequence, QPixmap

from background import Background
from carousel import Carousel
from detail_panel import DetailPanel

TOOL_ICON_DIR = Path(__file__).parent / "assets" / "tool_icons"


def _load_tool_icon(tool: dict) -> QPixmap | None:
    slug = re.sub(r'[^a-z0-9]+', '_', tool["name"].lower()).strip('_')
    path = TOOL_ICON_DIR / f"{slug}.png"
    if path.exists():
        pm = QPixmap(str(path))
        return pm if not pm.isNull() else None
    return None


_INACTIVE_BTN = """
    QPushButton {
        font-family: Consolas; font-size: 13px; font-weight: bold;
        border: 1px solid rgba(255,255,255,15); border-radius: 4px;
        background: rgba(255,255,255,6); color: rgba(255,255,255,50);
        padding: 0 6px;
    }
    QPushButton:hover { background: rgba(255,255,255,12); color: rgba(255,255,255,90); }
"""

_SCROLL_STYLE = """
    QScrollArea { border: none; background: transparent; }
    QScrollBar:vertical { width: 6px; background: transparent; border: none; }
    QScrollBar::handle:vertical { background: rgba(255,255,255,20); border-radius: 3px; min-height: 20px; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
"""


class _GridCard(QFrame):
    clicked = Signal(dict)

    def __init__(self, tool: dict, parent=None):
        super().__init__(parent)
        self.tool = tool
        self._selected = False
        self.setFixedHeight(250)
        self.setMinimumWidth(140)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 14)
        layout.setSpacing(10)

        accent = tool["accent"]
        r, g, b = accent.red(), accent.green(), accent.blue()

        # Icon
        icon_px = _load_tool_icon(tool)
        icon_lbl = QLabel()
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setFixedHeight(110)
        if icon_px:
            icon_lbl.setPixmap(icon_px.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            icon_lbl.setText(tool.get("icon_char", ""))
            icon_lbl.setStyleSheet(f"font-size: 64px; color: rgba({r},{g},{b},120);")
        layout.addWidget(icon_lbl)

        # Tag badge
        tag = QLabel(tool["tag"])
        tag.setStyleSheet(f"font-family: Consolas; font-size: 10px; font-weight: bold; "
                          f"letter-spacing: 2px; padding: 3px 10px; border-radius: 3px; "
                          f"background: rgba({r},{g},{b},40); color: {accent.name()};")
        layout.addWidget(tag)

        # Name
        name = QLabel(tool["name"])
        name.setStyleSheet("font-family: 'Segoe UI'; font-size: 15px; font-weight: bold; "
                           "color: rgba(220,230,255,220);")
        name.setWordWrap(True)
        layout.addWidget(name)

        layout.addStretch()

        # Install status
        installed = DetailPanel._is_installed(tool)
        status = QLabel("● INSTALLED" if installed else "○ NOT INSTALLED")
        status.setStyleSheet(f"font-family: Consolas; font-size: 9px; letter-spacing: 1px; "
                             f"color: {accent.name() if installed else 'rgba(255,255,255,25)'};")
        layout.addWidget(status)

        self._refresh()

    def _refresh(self):
        accent = self.tool["accent"]
        r, g, b = accent.red(), accent.green(), accent.blue()
        if self._selected:
            self.setStyleSheet(f"QFrame {{ border: 1px solid {accent.name()}; border-radius: 10px; "
                               f"background: rgba({r},{g},{b},18); }}")
        else:
            self.setStyleSheet("QFrame { border: 1px solid rgba(255,255,255,10); border-radius: 10px; "
                               "background: rgba(255,255,255,5); } "
                               "QFrame:hover { border: 1px solid rgba(255,255,255,25); "
                               "background: rgba(255,255,255,10); }")

    def set_selected(self, v: bool):
        if self._selected != v:
            self._selected = v
            self._refresh()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.tool)
        super().mousePressEvent(event)


class _ListRow(QFrame):
    clicked = Signal(dict)

    def __init__(self, tool: dict, parent=None):
        super().__init__(parent)
        self.tool = tool
        self._selected = False
        self.setFixedHeight(90)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 28, 0)
        layout.setSpacing(18)

        accent = tool["accent"]
        r, g, b = accent.red(), accent.green(), accent.blue()

        # Icon
        icon_lbl = QLabel()
        icon_lbl.setFixedSize(62, 62)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_px = _load_tool_icon(tool)
        if icon_px:
            icon_lbl.setPixmap(icon_px.scaled(58, 58, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            icon_lbl.setText(tool.get("icon_char", ""))
            icon_lbl.setStyleSheet(f"font-size: 34px; color: rgba({r},{g},{b},140);")
        layout.addWidget(icon_lbl)

        # Name + tag + desc
        text_col = QVBoxLayout()
        text_col.setSpacing(4)
        text_col.setContentsMargins(0, 0, 0, 0)

        name_lbl = QLabel(tool["name"])
        name_lbl.setStyleSheet("font-family: 'Segoe UI'; font-size: 16px; font-weight: bold; "
                               "color: rgba(220,230,255,220);")

        tag_and_desc = QHBoxLayout()
        tag_and_desc.setSpacing(10)
        tag_and_desc.setContentsMargins(0, 0, 0, 0)

        tag_lbl = QLabel(tool["tag"])
        tag_lbl.setStyleSheet(f"font-family: Consolas; font-size: 10px; font-weight: bold; "
                              f"letter-spacing: 1px; padding: 2px 7px; border-radius: 3px; "
                              f"background: rgba({r},{g},{b},40); color: {accent.name()};")
        desc_lbl = QLabel(tool["desc"])
        desc_lbl.setStyleSheet("font-family: 'Segoe UI'; font-size: 12px; color: rgba(150,170,210,160);")
        desc_lbl.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        tag_and_desc.addWidget(tag_lbl)
        tag_and_desc.addWidget(desc_lbl)
        tag_and_desc.addStretch()

        text_col.addWidget(name_lbl)
        text_col.addLayout(tag_and_desc)
        layout.addLayout(text_col, 1)

        # Install status
        installed = DetailPanel._is_installed(tool)
        status = QLabel("● INSTALLED" if installed else "○ NOT INSTALLED")
        status.setStyleSheet(f"font-family: Consolas; font-size: 10px; letter-spacing: 1px; "
                             f"color: {accent.name() if installed else 'rgba(255,255,255,25)'};")
        status.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(status)

        self._refresh()

    def _refresh(self):
        accent = self.tool["accent"]
        r, g, b = accent.red(), accent.green(), accent.blue()
        if self._selected:
            self.setStyleSheet(f"QFrame {{ border: 1px solid {accent.name()}; border-radius: 8px; "
                               f"background: rgba({r},{g},{b},12); }}")
        else:
            self.setStyleSheet("QFrame { border: 1px solid transparent; border-radius: 8px; "
                               "background: transparent; } "
                               "QFrame:hover { border: 1px solid rgba(255,255,255,10); "
                               "background: rgba(255,255,255,6); }")

    def set_selected(self, v: bool):
        if self._selected != v:
            self._selected = v
            self._refresh()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.tool)
        super().mousePressEvent(event)


class MainWindow(QWidget):
    back_requested = Signal()

    def __init__(self, game: dict):
        super().__init__()
        tools = game["tools"]
        self._tools      = tools
        self._view       = 0
        self._dots       = []
        self._grid_cards = []
        self._list_rows  = []
        self._view_btns  = []
        self._game_accent = game["accent"]

        # Background
        self.bg = Background(self)
        self.bg.setGeometry(self.rect())
        self.bg.set_accent(game["accent"])

        # Root layout
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        center = QVBoxLayout()
        center.setContentsMargins(0, 0, 0, 0)
        center.setSpacing(0)

        # ── Header ────────────────────────────────────────────────────────────
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet("background: transparent;")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(30, 0, 30, 0)
        h_layout.setSpacing(16)

        accent = game["accent"]
        r, g, b = accent.red(), accent.green(), accent.blue()

        back_btn = QPushButton("← GAMES")
        back_btn.setFixedHeight(28)
        back_btn.setStyleSheet(f"""
            QPushButton {{
                font-family: Consolas; font-size: 9px; font-weight: bold;
                letter-spacing: 2px; border: 1px solid rgba(255,255,255,15);
                border-radius: 4px; background: rgba(255,255,255,6);
                color: rgba(255,255,255,255); padding: 0 10px;
            }}
            QPushButton:hover {{
                background: rgba({r},{g},{b},20);
                border-color: rgba({r},{g},{b},80);
                color: rgb({r},{g},{b});
            }}
            QPushButton:pressed {{ background: rgba({r},{g},{b},35); }}
        """)
        back_btn.clicked.connect(self.back_requested.emit)
        h_layout.addWidget(back_btn)

        title = QLabel(game['short'].upper())
        title.setStyleSheet("""
            font-family: Consolas; font-size: 12px; font-weight: bold;
            letter-spacing: 3px; color: rgba(255,255,255,255);
        """)
        h_layout.addWidget(title)
        h_layout.addStretch()

        count_lbl = QLabel(f"{len(tools)} TOOL{'S' if len(tools) != 1 else ''}")
        count_lbl.setStyleSheet("""
            font-family: Consolas; font-size: 12px;
            letter-spacing: 2px; color: rgba(255,255,255,255);
        """)
        h_layout.addWidget(count_lbl)

        if tools:
            for icon, idx in (("⊙", 0), ("⊞", 1), ("☰", 2)):
                btn = QPushButton(icon)
                btn.setFixedSize(28, 28)
                self._view_btns.append(btn)
                h_layout.addWidget(btn)
                _idx = idx
                btn.clicked.connect(lambda _=False, i=_idx: self._set_view(i))
            self._update_view_btns()

        center.addWidget(header)

        # ── Content ───────────────────────────────────────────────────────────
        if tools:
            self.content_stack = QStackedWidget()

            # ── Page 0: Carousel ──────────────────────────────────────────────
            carousel_page = QWidget()
            cp = QVBoxLayout(carousel_page)
            cp.setContentsMargins(0, 0, 0, 0)
            cp.setSpacing(0)
            cp.addStretch(3)

            self.carousel = Carousel(tools)
            self.carousel.tool_changed.connect(self._on_tool_changed)
            cp.addWidget(self.carousel)
            cp.addStretch(1)

            nav_row = QHBoxLayout()
            nav_row.setContentsMargins(0, 0, 0, 16)
            nav_row.addStretch()

            self.prev_btn = QPushButton("◀")
            self.next_btn = QPushButton("▶")
            for btn in (self.prev_btn, self.next_btn):
                btn.setFixedSize(44, 44)
                btn.setStyleSheet("""
                    QPushButton {
                        font-size: 14px; border: 1px solid rgba(255,255,255,15);
                        border-radius: 22px; background: rgba(255,255,255,6);
                        color: rgba(255,255,255,80);
                    }
                    QPushButton:hover { background: rgba(255,255,255,15); color: white; }
                    QPushButton:pressed { background: rgba(255,255,255,25); }
                """)
            self.prev_btn.clicked.connect(self.carousel.go_prev)
            self.next_btn.clicked.connect(self.carousel.go_next)
            QShortcut(QKeySequence(Qt.Key_Left),  self).activated.connect(self.carousel.go_prev)
            QShortcut(QKeySequence(Qt.Key_Right), self).activated.connect(self.carousel.go_next)
            nav_row.addWidget(self.prev_btn)

            self.dots_layout = QHBoxLayout()
            self.dots_layout.setSpacing(8)
            for _ in tools:
                dot = QLabel("●")
                dot.setStyleSheet("font-size: 8px; color: rgba(255,255,255,20);")
                self.dots_layout.addWidget(dot)
                self._dots.append(dot)
            nav_row.addLayout(self.dots_layout)
            nav_row.addWidget(self.next_btn)
            nav_row.addStretch()

            nav_w = QWidget()
            nav_w.setLayout(nav_row)
            nav_w.setFixedHeight(60)
            cp.addWidget(nav_w)

            self.content_stack.addWidget(carousel_page)

            # ── Page 1: Grid ──────────────────────────────────────────────────
            grid_scroll = QScrollArea()
            grid_scroll.setWidgetResizable(True)
            grid_scroll.setStyleSheet(_SCROLL_STYLE)
            grid_scroll.viewport().setStyleSheet("background: transparent;")
            grid_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

            grid_container = QWidget()
            grid_container.setStyleSheet("background: transparent;")
            grid_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            grid_layout = QGridLayout(grid_container)
            grid_layout.setContentsMargins(40, 30, 40, 30)
            grid_layout.setSpacing(16)
            grid_layout.setAlignment(Qt.AlignTop)

            cols = 5
            for c in range(cols):
                grid_layout.setColumnStretch(c, 1)
            for i, tool in enumerate(tools):
                card = _GridCard(tool)
                card.clicked.connect(self._on_tool_changed)
                grid_layout.addWidget(card, i // cols, i % cols)
                self._grid_cards.append(card)

            grid_scroll.setWidget(grid_container)
            self.content_stack.addWidget(grid_scroll)

            # ── Page 2: List ──────────────────────────────────────────────────
            list_scroll = QScrollArea()
            list_scroll.setWidgetResizable(True)
            list_scroll.setStyleSheet(_SCROLL_STYLE)
            list_scroll.viewport().setStyleSheet("background: transparent;")
            list_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

            list_container = QWidget()
            list_container.setStyleSheet("background: transparent;")
            list_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            list_layout = QVBoxLayout(list_container)
            list_layout.setContentsMargins(40, 20, 40, 20)
            list_layout.setSpacing(4)
            list_layout.setAlignment(Qt.AlignTop)

            for tool in tools:
                row = _ListRow(tool)
                row.clicked.connect(self._on_tool_changed)
                list_layout.addWidget(row)
                self._list_rows.append(row)

            list_scroll.setWidget(list_container)
            self.content_stack.addWidget(list_scroll)

            center.addWidget(self.content_stack, 1)

            self.detail = DetailPanel()
            self.detail.setStyleSheet("background: rgba(0,0,0,0);")
            self._on_tool_changed(tools[0])

        else:
            coming = QLabel("COMING SOON")
            coming.setAlignment(Qt.AlignCenter)
            coming.setStyleSheet("""
                font-family: Consolas; font-size: 18px; font-weight: bold;
                letter-spacing: 6px; color: rgba(255,255,255,20);
            """)
            center.addWidget(coming, 1)
            self.detail = DetailPanel()
            self.detail.setStyleSheet("background: rgba(0,0,0,0);")

        root.addLayout(center, 1)
        root.addWidget(self.detail)

    # ── View switching ─────────────────────────────────────────────────────────

    def _set_view(self, idx: int):
        self._view = idx
        self.content_stack.setCurrentIndex(idx)
        self._update_view_btns()

    def _update_view_btns(self):
        accent = self._game_accent
        r, g, b = accent.red(), accent.green(), accent.blue()
        active = (f"QPushButton {{ font-family: Consolas; font-size: 13px; font-weight: bold; "
                  f"border: 1px solid {accent.name()}; border-radius: 4px; "
                  f"background: rgba({r},{g},{b},20); color: {accent.name()}; padding: 0 6px; }}")
        for i, btn in enumerate(self._view_btns):
            btn.setStyleSheet(active if i == self._view else _INACTIVE_BTN)

    # ── Tool selection ─────────────────────────────────────────────────────────

    def _on_tool_changed(self, tool: dict):
        self.bg.set_accent(tool["accent"])
        self.detail.show_tool(tool)

        idx = self._tools.index(tool)

        for i, dot in enumerate(self._dots):
            col = tool["accent"].name() if i == idx else "rgba(255,255,255,20)"
            dot.setStyleSheet(f"font-size: 8px; color: {col};")

        for i, card in enumerate(self._grid_cards):
            card.set_selected(i == idx)

        for i, row in enumerate(self._list_rows):
            row.set_selected(i == idx)

    def resizeEvent(self, event):
        self.bg.setGeometry(self.rect())
        super().resizeEvent(event)
