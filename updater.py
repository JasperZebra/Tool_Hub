import re
import sys
import urllib.request
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal

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
    print(f"[updater] DEBUG: fetching {url}", flush=True)
    try:
        with urllib.request.urlopen(url, timeout=8) as r:
            text = r.read(8192).decode("utf-8", errors="ignore")
        print(f"[updater] DEBUG: got {len(text)} bytes", flush=True)
        m = re.search(r"APP_VERSION\s*=\s*\((\d+),\s*(\d+),\s*(\d+)\)", text)
        if m:
            ver = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
            print(f"[updater] DEBUG: remote={ver} local={APP_VERSION}", flush=True)
            return ver
        print("[updater] DEBUG: APP_VERSION not found in remote", flush=True)
    except Exception as e:
        print(f"[updater] DEBUG: fetch error: {e}", flush=True)
    return None


class _CheckWorker(QObject):
    finished = Signal(str, object)

    def run(self):
        print("[updater] DEBUG: _CheckWorker.run() started", flush=True)
        remote = _fetch_remote_version()
        if remote is None:
            self.finished.emit("error", None)
        elif remote > APP_VERSION:
            print(f"[updater] DEBUG: update_available!", flush=True)
            self.finished.emit("update_available", remote)
        else:
            print(f"[updater] DEBUG: up_to_date", flush=True)
            self.finished.emit("up_to_date", remote)


class _ApplyWorker(QObject):
    progress = Signal(int, int)
    finished = Signal(object)

    def run(self):
        print(f"[updater] DEBUG: _ApplyWorker.run() started", flush=True)
        failed = []
        total = len(_ALL_FILES)
        for i, rel_path in enumerate(_ALL_FILES, 1):
            url  = _RAW_BASE + rel_path
            base = _PY_DIR if rel_path.endswith(".py") else _ASSET_DIR
            dest = base / Path(rel_path)
            print(f"[updater] DEBUG: ({i}/{total}) {rel_path}", flush=True)
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                with urllib.request.urlopen(url, timeout=30) as r:
                    dest.write_bytes(r.read())
            except Exception as e:
                print(f"[updater] DEBUG: FAILED {rel_path}: {e}", flush=True)
                failed.append(f"{rel_path}: {e}")
            self.progress.emit(i, total)
        print(f"[updater] DEBUG: apply done failures={failed}", flush=True)
        self.finished.emit(failed)


def start_check(on_result) -> QThread:
    print("[updater] DEBUG: start_check() called", flush=True)
    thread = QThread()
    worker = _CheckWorker()
    # Connect output signals before moveToThread, started after
    worker.finished.connect(on_result)
    worker.finished.connect(thread.quit)
    thread.finished.connect(thread.deleteLater)
    thread.finished.connect(worker.deleteLater)
    worker.moveToThread(thread)
    thread.started.connect(worker.run)
    thread.start()
    print("[updater] DEBUG: check thread started", flush=True)
    return thread


def start_apply(on_progress, on_finished) -> QThread:
    print("[updater] DEBUG: start_apply() called", flush=True)
    thread = QThread()
    worker = _ApplyWorker()
    worker.progress.connect(on_progress)
    worker.finished.connect(on_finished)
    worker.finished.connect(thread.quit)
    thread.finished.connect(thread.deleteLater)
    thread.finished.connect(worker.deleteLater)
    worker.moveToThread(thread)
    thread.started.connect(worker.run)
    thread.start()
    print("[updater] DEBUG: apply thread started", flush=True)
    return thread