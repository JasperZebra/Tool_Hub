import re
import sys
import threading
import urllib.request
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtWidgets import QDialog, QLabel, QProgressBar, QVBoxLayout, QApplication

# ── Version ────────────────────────────────────────────────────────────────────
APP_VERSION = (0, 1, 1)

# ── Config ─────────────────────────────────────────────────────────────────────
_RAW_BASE = "https://raw.githubusercontent.com/JasperZebra/Tool_Hub/main/"

_PY_FILES = [
    "anim.py", "background.py", "card.py", "carousel.py",
    "detail_panel.py", "downloader.py", "game_data.py",
    "game_select.py", "main.py", "main_window.py", "paths.py", "updater.py",
]

_ASSET_FILES = [
    "assets/main_tool_icon/tool_hub.ico",
    "assets/game_icons/afop.png",
    "assets/game_icons/atg_09.png",
    "assets/game_icons/fc2.png",
    "assets/tool_icons/afop_banshee_skin_color_editor.png",
    "assets/tool_icons/afop_camocolorpalette_editor.png",
    "assets/tool_icons/afop_eye_color_editor.png",
    "assets/tool_icons/afop_hair_color_editor.png",
    "assets/tool_icons/afop_skin_color_editor.png",
    "assets/tool_icons/afop_warpaint_color_editor.png",
    "assets/tool_icons/file_editor.png",
    "assets/tool_icons/level_editor.png",
    "assets/tool_icons/mod_manager.png",
    "assets/tool_icons/save_editor.png",
    "assets/tool_icons/xbg_extractor.png",
    "assets/tool_icons/xbm_editor.png",
]

_ALL_FILES = _PY_FILES + _ASSET_FILES

if getattr(sys, "frozen", False):
    _EXE_DIR   = Path(sys.executable).parent
    _PY_DIR    = _EXE_DIR / "lib"
    _ASSET_DIR = _EXE_DIR
else:
    _PY_DIR    = Path(__file__).parent
    _ASSET_DIR = Path(__file__).parent


def fmt_version(v: tuple) -> str:
    return f"v{v[0]}.{v[1]}.{v[2]}"


def _fetch_remote_version() -> tuple | None:
    url = _RAW_BASE + "updater.py"
    try:
        with urllib.request.urlopen(url, timeout=8) as r:
            text = r.read(8192).decode("utf-8", errors="ignore")
        m = re.search(r"APP_VERSION\s*=\s*\((\d+),\s*(\d+),\s*(\d+)\)", text)
        if m:
            return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except Exception as e:
        print(f"[updater] fetch error: {e}", flush=True)
    return None


# ── Signal bridge ──────────────────────────────────────────────────────────────

class _Bridge(QObject):
    check_done     = Signal(str, object)
    apply_progress = Signal(int, int)
    apply_done     = Signal(object)

_bridge = _Bridge()


# ── Progress dialog — modal, no close button ───────────────────────────────────

class _ProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Downloading Update")
        self.setWindowFlags(
            Qt.Dialog |
            Qt.CustomizeWindowHint |
            Qt.WindowTitleHint
            # no Qt.WindowCloseButtonHint → close button disabled
        )
        self.setFixedWidth(440)
        self.setModal(True)

        self._title = QLabel("Downloading update, please do not close…")
        self._title.setAlignment(Qt.AlignCenter)
        self._title.setStyleSheet("font-family: Consolas; font-size: 11px; color: rgba(200,220,255,220);")

        self._bar = QProgressBar()
        self._bar.setRange(0, len(_ALL_FILES))
        self._bar.setValue(0)
        self._bar.setTextVisible(True)

        self._file_lbl = QLabel("Starting…")
        self._file_lbl.setAlignment(Qt.AlignCenter)
        self._file_lbl.setStyleSheet("font-family: Consolas; font-size: 9px; color: rgba(150,180,220,160);")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)
        layout.addWidget(self._title)
        layout.addWidget(self._bar)
        layout.addWidget(self._file_lbl)

    def closeEvent(self, event):
        # Block close while downloading
        event.ignore()

    def set_progress(self, done: int, total: int):
        self._bar.setValue(done)
        if 0 < done <= len(_ALL_FILES):
            self._file_lbl.setText(_ALL_FILES[done - 1])

    def mark_done(self, failed: list):
        # Re-enable closing once done
        self.closeEvent = lambda e: e.accept()
        if failed:
            self._title.setText("⚠  Some files failed to download.")
            self._file_lbl.setText("\n".join(failed[:5]))
        else:
            self._title.setText("✓  Update complete — please restart Tool Hub.")
            self._file_lbl.setText("")
        self._bar.setValue(len(_ALL_FILES))
        from PySide6.QtCore import QTimer
        QTimer.singleShot(1000, self.accept)


# ── Public API ─────────────────────────────────────────────────────────────────

def start_check(on_result) -> threading.Thread:
    _bridge.check_done.connect(on_result)

    def _run():
        remote = _fetch_remote_version()
        if remote is None:
            _bridge.check_done.emit("error", None)
        elif remote > APP_VERSION:
            _bridge.check_done.emit("update_available", remote)
        else:
            _bridge.check_done.emit("up_to_date", remote)

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return t


def start_apply(on_progress, on_finished, parent=None) -> threading.Thread:
    """
    Shows a modal progress dialog that blocks the user from closing the app
    mid-download. on_progress and on_finished are still called as before.
    """
    dlg = _ProgressDialog(parent)
    dlg.show()

    def _on_progress(done: int, total: int):
        dlg.set_progress(done, total)
        on_progress(done, total)

    def _on_done(failed: list):
        dlg.mark_done(failed)
        on_finished(failed)

    _bridge.apply_progress.connect(_on_progress)
    _bridge.apply_done.connect(_on_done)

    def _run():
        failed = []
        total = len(_ALL_FILES)
        for i, rel_path in enumerate(_ALL_FILES, 1):
            url  = _RAW_BASE + rel_path
            base = _PY_DIR if rel_path.endswith(".py") else _ASSET_DIR
            dest = base / Path(rel_path)
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                with urllib.request.urlopen(url, timeout=30) as r:
                    dest.write_bytes(r.read())
            except Exception as e:
                print(f"[updater] FAILED {rel_path}: {e}", flush=True)
                failed.append(f"{rel_path}: {e}")
            _bridge.apply_progress.emit(i, total)
        _bridge.apply_done.emit(failed)

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return t