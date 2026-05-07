import os
import re
import sys
import urllib.request
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal, Qt
from PySide6.QtWidgets import (
    QDialog, QLabel, QProgressBar, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QApplication,
)

# ── Version ────────────────────────────────────────────────────────────────────
APP_VERSION = (0, 1, 1)

# ── Config ─────────────────────────────────────────────────────────────────────
_RAW_BASE = "https://raw.githubusercontent.com/JasperZebra/Tool_Hub/main/"

_PY_FILES = [
    "anim.py",
    "background.py",
    "card.py",
    "carousel.py",
    "detail_panel.py",
    "downloader.py",
    "game_data.py",
    "game_select.py",
    "main.py",
    "main_window.py",
    "paths.py",
    "updater.py",
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


# ── Remote version fetch ───────────────────────────────────────────────────────

def _fetch_remote_version() -> tuple | None:
    url = _RAW_BASE + "updater.py"
    print(f"[updater] DEBUG: fetching remote version from {url}", flush=True)
    try:
        with urllib.request.urlopen(url, timeout=8) as r:
            text = r.read(8192).decode("utf-8", errors="ignore")
        print(f"[updater] DEBUG: fetched {len(text)} bytes from remote", flush=True)
        m = re.search(r"APP_VERSION\s*=\s*\((\d+),\s*(\d+),\s*(\d+)\)", text)
        if m:
            ver = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
            print(f"[updater] DEBUG: remote APP_VERSION = {ver}", flush=True)
            return ver
        else:
            print("[updater] DEBUG: APP_VERSION pattern NOT found in remote file", flush=True)
    except Exception as e:
        print(f"[updater] DEBUG: network error fetching remote version: {e}", flush=True)
    return None


# ── Background workers ─────────────────────────────────────────────────────────

class _CheckWorker(QObject):
    finished = Signal(str, object)

    def run(self):
        print("[updater] DEBUG: _CheckWorker.run() started", flush=True)
        remote = _fetch_remote_version()
        if remote is None:
            print("[updater] DEBUG: result = error (could not fetch remote)", flush=True)
            self.finished.emit("error", None)
        elif remote > APP_VERSION:
            print(f"[updater] DEBUG: result = update_available  local={APP_VERSION}  remote={remote}", flush=True)
            self.finished.emit("update_available", remote)
        else:
            print(f"[updater] DEBUG: result = up_to_date  local={APP_VERSION}  remote={remote}", flush=True)
            self.finished.emit("up_to_date", remote)


class _ApplyWorker(QObject):
    progress = Signal(int, int)
    finished = Signal(object)

    def run(self):
        print(f"[updater] DEBUG: _ApplyWorker.run() started — {len(_ALL_FILES)} files to download", flush=True)
        failed = []
        total = len(_ALL_FILES)
        for i, rel_path in enumerate(_ALL_FILES, 1):
            url  = _RAW_BASE + rel_path
            base = _PY_DIR if rel_path.endswith(".py") else _ASSET_DIR
            dest = base / Path(rel_path)
            print(f"[updater] DEBUG: downloading ({i}/{total}) {rel_path} → {dest}", flush=True)
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                with urllib.request.urlopen(url, timeout=30) as r:
                    dest.write_bytes(r.read())
                print(f"[updater] DEBUG: OK {rel_path}", flush=True)
            except Exception as e:
                print(f"[updater] DEBUG: FAILED {rel_path}: {e}", flush=True)
                failed.append(f"{rel_path}: {e}")
            self.progress.emit(i, total)
        print(f"[updater] DEBUG: _ApplyWorker done. failures={failed}", flush=True)
        self.finished.emit(failed)


# ── Progress dialog ────────────────────────────────────────────────────────────

class _ProgressDialog(QDialog):
    def __init__(self, remote_ver: tuple, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Updating Tool Hub")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)
        self.setFixedWidth(420)
        self.setModal(True)

        self._label = QLabel(f"Downloading update {fmt_version(remote_ver)}…")
        self._label.setAlignment(Qt.AlignCenter)

        self._bar = QProgressBar()
        self._bar.setRange(0, len(_ALL_FILES))
        self._bar.setValue(0)
        self._bar.setTextVisible(True)

        self._file_label = QLabel("Starting…")
        self._file_label.setAlignment(Qt.AlignCenter)
        self._file_label.setStyleSheet("color: grey; font-size: 11px;")

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.addWidget(self._label)
        layout.addWidget(self._bar)
        layout.addWidget(self._file_label)

    def set_progress(self, done: int, total: int):
        self._bar.setValue(done)
        if 0 < done <= len(_ALL_FILES):
            self._file_label.setText(_ALL_FILES[done - 1])


# ── Public API ─────────────────────────────────────────────────────────────────

def start_check(on_result) -> QThread:
    print("[updater] DEBUG: start_check() called — spawning _CheckWorker thread", flush=True)
    thread = QThread()
    worker = _CheckWorker()
    worker.moveToThread(thread)
    thread.started.connect(worker.run)
    worker.finished.connect(on_result)
    worker.finished.connect(thread.quit)
    thread.finished.connect(thread.deleteLater)
    thread.finished.connect(worker.deleteLater)
    thread.start()
    return thread


def start_apply(on_progress, on_finished) -> QThread:
    print("[updater] DEBUG: start_apply() called — spawning _ApplyWorker thread", flush=True)
    thread = QThread()
    worker = _ApplyWorker()
    worker.moveToThread(thread)
    thread.started.connect(worker.run)
    worker.progress.connect(on_progress)
    worker.finished.connect(on_finished)
    worker.finished.connect(thread.quit)
    thread.finished.connect(thread.deleteLater)
    thread.finished.connect(worker.deleteLater)
    thread.start()
    return thread


def check_and_prompt(parent=None) -> None:
    """
    Call once from main.py after window.show().
    Silently checks remote APP_VERSION; prompts + downloads if newer.
    """
    print(f"[updater] DEBUG: check_and_prompt() called. Local APP_VERSION={APP_VERSION}", flush=True)
    _state = {}

    def _on_check(status: str, remote_ver):
        print(f"[updater] DEBUG: _on_check() fired — status={status!r}  remote_ver={remote_ver}", flush=True)
        if status != "update_available":
            print("[updater] DEBUG: no update needed, doing nothing", flush=True)
            return

        current_str = fmt_version(APP_VERSION)
        remote_str  = fmt_version(remote_ver)
        print(f"[updater] DEBUG: showing QMessageBox ({current_str} → {remote_str})", flush=True)

        reply = QMessageBox.question(
            parent,
            "Update Available",
            f"A new version of Tool Hub is available.\n\n"
            f"  Installed : {current_str}\n"
            f"  Available : {remote_str}\n\n"
            "Download and install now?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        print(f"[updater] DEBUG: user replied {'Yes' if reply == QMessageBox.Yes else 'No'}", flush=True)
        if reply != QMessageBox.Yes:
            return

        dlg = _ProgressDialog(remote_ver, parent)
        dlg.show()
        _state["dlg"] = dlg

        def _on_progress(done: int, total: int):
            print(f"[updater] DEBUG: progress {done}/{total}", flush=True)
            dlg.set_progress(done, total)

        def _on_finished(failed: list):
            print(f"[updater] DEBUG: apply finished. failed={failed}", flush=True)
            dlg.accept()
            if failed:
                err_list = "\n".join(failed[:10])
                QMessageBox.warning(
                    parent,
                    "Update Incomplete",
                    f"Some files could not be downloaded:\n\n{err_list}\n\n"
                    "Please try again later or download manually from GitHub.",
                )
            else:
                QMessageBox.information(
                    parent,
                    "Update Complete",
                    f"Tool Hub has been updated to {remote_str}.\n\n"
                    "Please restart the application to use the new version.",
                )
                QApplication.quit()

        _state["thread"] = start_apply(_on_progress, _on_finished)

    _state["check_thread"] = start_check(_on_check)
    print(f"[updater] DEBUG: check thread started. _state keys={list(_state.keys())}", flush=True)
    return _state  # caller MUST hold this reference or threads get GC'd