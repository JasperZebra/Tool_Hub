import subprocess

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from downloader import Downloader


class DetailPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(260)
        self._tool = None
        # folder (Path) -> {"downloader": Downloader, "pct": int, "error": bool}
        self._downloads = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 30, 20, 30)
        layout.setSpacing(16)

        self.tag_lbl = QLabel("")
        self.tag_lbl.setStyleSheet("""
            font-family: Consolas;
            font-size: 9px;
            font-weight: bold;
            letter-spacing: 3px;
            padding: 3px 8px;
            border-radius: 3px;
        """)
        self.tag_lbl.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.tag_lbl)

        self.name_lbl = QLabel("")
        self.name_lbl.setStyleSheet("""
            font-family: 'Segoe UI';
            font-size: 20px;
            font-weight: 700;
            color: #f0f4ff;
        """)
        self.name_lbl.setWordWrap(True)
        layout.addWidget(self.name_lbl)

        self.desc_lbl = QLabel("")
        self.desc_lbl.setStyleSheet("""
            font-family: 'Segoe UI';
            font-size: 11px;
            color: #8899bb;
            line-height: 1.5;
        """)
        self.desc_lbl.setWordWrap(True)
        layout.addWidget(self.desc_lbl)

        # Stats grid
        self.stats_frame = QFrame()
        self.stats_frame.setStyleSheet("background: rgba(255,255,255,6); border-radius: 8px;")
        self.stats_layout = QVBoxLayout(self.stats_frame)
        self.stats_layout.setContentsMargins(12, 10, 12, 10)
        self.stats_layout.setSpacing(8)
        layout.addWidget(self.stats_frame)

        layout.addStretch()

        self.launch_btn = QPushButton("▶  LAUNCH TOOL")
        self.launch_btn.setFixedHeight(40)
        self.launch_btn.clicked.connect(self._on_btn_clicked)
        layout.addWidget(self.launch_btn)

    # ── Installation / exe helpers ─────────────────────────────────────────────

    @staticmethod
    def _is_installed(tool: dict) -> bool:
        folder = tool.get("folder")
        if not folder or not folder.exists():
            return False
        return any(f for f in folder.iterdir() if f.name != "version.json")

    @staticmethod
    def _has_exe(tool: dict) -> bool:
        return bool(tool.get("exe", ""))

    # ── Button handler ─────────────────────────────────────────────────────────

    def _on_btn_clicked(self):
        if not self._tool:
            return
        folder = self._tool["folder"]

        if self._is_installed(self._tool):
            exe_name = self._tool.get("exe", "")
            if exe_name:
                subprocess.Popen([str(folder / exe_name)], cwd=str(folder))
            else:
                subprocess.Popen(["explorer", str(folder)])
            return

        has_source = bool(self._tool.get("repo", "") or self._tool.get("zip_url", ""))
        if self._tool.get("coming_soon") or not has_source:
            return

        # Already downloading — ignore extra clicks
        if folder in self._downloads:
            return

        self._start_download(self._tool)

    # ── Per-tool download management ───────────────────────────────────────────

    def _start_download(self, tool: dict):
        folder = tool["folder"]
        dl = Downloader(self)
        self._downloads[folder] = {"downloader": dl, "pct": -1, "error": False}

        dl.progress.connect(lambda pct, f=folder: self._on_progress(f, pct))
        dl.finished.connect(lambda tag, f=folder: self._on_finished(f, tag))
        dl.error.connect(lambda msg, f=folder: self._on_error(f, msg))

        dl.start(tool)

        if self._tool and self._tool["folder"] == folder:
            self._set_btn_connecting()

    def _on_progress(self, folder, pct: int):
        if folder in self._downloads:
            self._downloads[folder]["pct"] = pct
        if self._tool and self._tool["folder"] == folder:
            self._set_btn_downloading(pct)

    def _on_finished(self, folder, tag: str):
        self._downloads.pop(folder, None)
        if self._tool and self._tool["folder"] == folder:
            self.show_tool(self._tool)

    def _on_error(self, folder, msg: str):
        self._downloads.pop(folder, None)
        if self._tool and self._tool["folder"] == folder:
            self.launch_btn.setText("✕  DOWNLOAD FAILED")
            self.launch_btn.setEnabled(True)

    # ── Button state helpers ───────────────────────────────────────────────────

    def _set_btn_connecting(self):
        self.launch_btn.setText("⬇  CONNECTING...")
        self.launch_btn.setEnabled(False)
        self._apply_btn_fill(0)

    def _set_btn_downloading(self, pct: int):
        if pct <= 100:
            label = f"⬇  DOWNLOADING  {pct}%"
            fill  = pct / 100
        else:
            label = f"⬇  EXTRACTING  {pct - 100}%"
            fill  = (pct - 100) / 100
        self.launch_btn.setText(label)
        self.launch_btn.setEnabled(False)
        self._apply_btn_fill(fill)

    def _apply_btn_fill(self, fill: float):
        if not self._tool:
            return
        accent = self._tool["accent"]
        r, g, b = accent.red(), accent.green(), accent.blue()
        hex_col  = accent.name()
        fill_col = f"rgba({r},{g},{b},90)"
        edge = max(0.0001, min(0.9999, fill))
        self.launch_btn.setStyleSheet(f"""
            QPushButton {{
                font-family: Consolas; font-size: 11px; font-weight: bold;
                letter-spacing: 2px;
                border: 1px solid {hex_col};
                border-radius: 6px; padding: 0 20px;
                color: {hex_col};
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {fill_col},
                    stop:{edge:.4f} {fill_col},
                    stop:{min(edge + 0.0001, 1.0):.4f} rgba(0,0,0,0),
                    stop:1 rgba(0,0,0,0));
            }}
        """)

    def _apply_btn_style(self, installed: bool):
        accent = self._tool["accent"]
        hex_col  = accent.name()
        dark_col = QColor(accent.red() // 4, accent.green() // 4, accent.blue() // 4)

        if self._tool.get("coming_soon"):
            self.launch_btn.setText("⧗  COMING SOON")
            self.launch_btn.setEnabled(False)
            self.launch_btn.setStyleSheet("""
                QPushButton {
                    font-family: Consolas; font-size: 11px; font-weight: bold;
                    letter-spacing: 2px; border: 1px solid rgba(255,255,255,12);
                    border-radius: 6px; padding: 0 20px;
                    background: transparent; color: rgba(255,255,255,25);
                }
            """)
        elif installed:
            label = "▶  LAUNCH TOOL" if self._has_exe(self._tool) else "⊞  OPEN FOLDER"
            self.launch_btn.setText(label)
            self.launch_btn.setEnabled(True)
            self.launch_btn.setStyleSheet(f"""
                QPushButton {{
                    font-family: Consolas; font-size: 11px; font-weight: bold;
                    letter-spacing: 2px; border: none; border-radius: 6px;
                    padding: 0 20px; background: {hex_col}; color: #050810;
                }}
                QPushButton:hover {{ background: white; }}
                QPushButton:pressed {{ background: {dark_col.name()}; color: {hex_col}; }}
            """)
        else:
            self.launch_btn.setText("⬇  DOWNLOAD TOOL")
            self.launch_btn.setEnabled(True)
            self.launch_btn.setStyleSheet(f"""
                QPushButton {{
                    font-family: Consolas; font-size: 11px; font-weight: bold;
                    letter-spacing: 2px; border: 1px solid {hex_col};
                    border-radius: 6px; padding: 0 20px;
                    background: transparent; color: {hex_col};
                }}
                QPushButton:hover {{ background: {dark_col.name()}; }}
                QPushButton:pressed {{ background: {hex_col}; color: #050810; }}
            """)

    # ── Public ─────────────────────────────────────────────────────────────────

    def show_tool(self, tool: dict):
        self._tool = tool
        accent: QColor = tool["accent"]
        hex_col  = accent.name()
        dark_col = QColor(accent.red() // 4, accent.green() // 4, accent.blue() // 4)

        game_accent: QColor = tool.get("game_accent", accent)
        g_hex  = game_accent.name()
        g_dark = QColor(game_accent.red() // 4, game_accent.green() // 4, game_accent.blue() // 4)
        self.tag_lbl.setText(tool["tag"])
        self.tag_lbl.setStyleSheet(f"""
            font-family: Consolas; font-size: 9px; font-weight: bold;
            letter-spacing: 3px; padding: 3px 8px; border-radius: 3px;
            background: {g_dark.name()}; color: {g_hex};
        """)

        self.name_lbl.setText(tool["name"])
        self.name_lbl.setStyleSheet("""
            font-family: 'Segoe UI'; font-size: 20px;
            font-weight: 700; color: #f0f4ff;
        """)

        self.desc_lbl.setText(tool["desc"])

        for i in reversed(range(self.stats_layout.count())):
            w = self.stats_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        for label, val in tool["stats"]:
            row = QHBoxLayout()
            lbl = QLabel(label.upper())
            lbl.setStyleSheet("font-family: Consolas; font-size: 9px; letter-spacing: 1px; color: #556688;")
            val_lbl = QLabel(val)
            val_lbl.setStyleSheet(f"font-family: 'Segoe UI'; font-size: 11px; font-weight: bold; color: {hex_col};")
            val_lbl.setAlignment(Qt.AlignRight)
            row.addWidget(lbl)
            row.addWidget(val_lbl)
            container = QWidget()
            container.setLayout(row)
            self.stats_layout.addWidget(container)

        # Restore in-progress state if this tool is already downloading
        folder = tool["folder"]
        if folder in self._downloads:
            pct = self._downloads[folder]["pct"]
            if pct < 0:
                self._set_btn_connecting()
            else:
                self._set_btn_downloading(pct)
        else:
            self._apply_btn_style(self._is_installed(tool))
