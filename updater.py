import re
import sys
import urllib.request
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal

# ── Version ────────────────────────────────────────────────────────────────────
# Bump this tuple when releasing a new version of the launcher.
APP_VERSION = (0, 1, 6)

# ── Config ─────────────────────────────────────────────────────────────────────
# Raw GitHub URL pointing to the main branch of the Tool Hub repo.
# Change OWNER and REPO to match your GitHub repository.
_RAW_BASE = "https://raw.githubusercontent.com/JasperZebra/Tool_Hub/main/"

# Launcher .py files to download on update. Does NOT touch anything under tools/.
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

# Asset files (PNGs) to download on update.
# Add new entries here whenever a new icon is pushed to the repo.
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

# cx_Freeze puts loose .py files in lib/ next to the exe.
# Assets (icons etc.) live in the exe's root folder.
if getattr(sys, "frozen", False):
    _EXE_DIR   = Path(sys.executable).parent   # build/Tool_Hub/
    _PY_DIR    = _EXE_DIR / "lib"              # build/Tool_Hub/lib/  ← where .py files live
    _ASSET_DIR = _EXE_DIR                      # build/Tool_Hub/      ← where assets/ lives
else:
    _PY_DIR    = Path(__file__).parent
    _ASSET_DIR = Path(__file__).parent


def fmt_version(v: tuple) -> str:
    return f"v{v[0]}.{v[1]}.{v[2]}"


def _fetch_remote_version() -> tuple | None:
    """Read updater.py from the remote repo and parse APP_VERSION out of it."""
    try:
        url = _RAW_BASE + "updater.py"
        with urllib.request.urlopen(url, timeout=8) as r:
            text = r.read(8192).decode("utf-8", errors="ignore")
        m = re.search(r"APP_VERSION\s*=\s*\((\d+),\s*(\d+),\s*(\d+)\)", text)
        if m:
            return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except Exception:
        pass
    return None


# ── Background: version check ──────────────────────────────────────────────────

class _CheckWorker(QObject):
    # status: "up_to_date" | "update_available" | "error"
    finished = Signal(str, object)   # (status, remote_ver tuple or None)

    def run(self):
        remote = _fetch_remote_version()
        if remote is None:
            self.finished.emit("error", None)
        elif remote > APP_VERSION:
            self.finished.emit("update_available", remote)
        else:
            self.finished.emit("up_to_date", remote)


# ── Background: apply update ───────────────────────────────────────────────────

class _ApplyWorker(QObject):
    progress = Signal(int, int)   # (files_done, files_total)
    finished = Signal(object)     # list[str] of "file: error" entries

    def run(self):
        failed = []
        total = len(_ALL_FILES)
        for i, rel_path in enumerate(_ALL_FILES, 1):
            url  = _RAW_BASE + rel_path
            # .py files go into lib/, everything else (assets) goes into the exe root
            base = _PY_DIR if rel_path.endswith(".py") else _ASSET_DIR
            dest = base / Path(rel_path)
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                with urllib.request.urlopen(url, timeout=30) as r:
                    dest.write_bytes(r.read())
            except Exception as e:
                failed.append(f"{rel_path}: {e}")
            self.progress.emit(i, total)
        self.finished.emit(failed)


# ── Public helpers ─────────────────────────────────────────────────────────────

def start_check(on_result) -> QThread:
    """
    Fire a background version check.
    on_result(status: str, remote_ver: tuple | None) is called on the Qt thread.
    Keep the returned QThread reference alive until it finishes.
    """
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
    """
    Fire a background update download.
    on_progress(done: int, total: int) and on_finished(failed: list) called on Qt thread.
    Keep the returned QThread reference alive until it finishes.
    """
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