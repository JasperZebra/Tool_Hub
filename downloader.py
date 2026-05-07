import json
import shutil
import time
import zipfile
import urllib.request
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal

GITHUB_API = "https://api.github.com/repos/{repo}/releases/latest"


# ── Version helpers ────────────────────────────────────────────────────────────

def get_installed_version(folder: Path) -> str | None:
    """Return the installed version tag, or None if not installed."""
    try:
        return json.loads((folder / "version.json").read_text())["tag"]
    except Exception:
        return None


def _save_version(folder: Path, tag: str):
    (folder / "version.json").write_text(json.dumps({"tag": tag}))


# ── GitHub API ─────────────────────────────────────────────────────────────────

def fetch_latest_release(repo: str) -> dict | None:
    """Hit the GitHub releases API and return the latest release dict, or None on failure."""
    try:
        req = urllib.request.Request(
            GITHUB_API.format(repo=repo),
            headers={"Accept": "application/vnd.github+json"},
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def check_status(tool: dict) -> tuple[str, dict | None]:
    """
    Return (status, release) where status is one of:
      "not_installed"  — folder empty, repo set
      "up_to_date"     — installed version matches latest
      "update_available" — installed but outdated
      "no_repo"        — repo field is empty, can only launch locally
      "api_error"      — couldn't reach GitHub
    """
    repo = tool.get("repo", "")
    folder: Path = tool.get("folder")

    if not repo:
        return "no_repo", None

    release = fetch_latest_release(repo)
    if release is None:
        return "api_error", None

    installed = get_installed_version(folder) if folder else None
    if installed is None:
        return "not_installed", release
    if installed != release["tag_name"]:
        return "update_available", release
    return "up_to_date", release


# ── Download worker ────────────────────────────────────────────────────────────

def _find_zip_asset(release: dict) -> dict | None:
    for asset in release.get("assets", []):
        if asset["name"].lower().endswith(".zip"):
            return asset
    return None


def _extract_flat(zip_path: Path, dest: Path, progress_cb=None):
    """
    Extract .zip into dest, stripping a single top-level directory if present
    (common on GitHub releases). Calls progress_cb(done, total) per file.
    """
    with zipfile.ZipFile(zip_path, "r") as zf:
        members = zf.infolist()
        names   = [m.filename for m in members]
        tops    = {n.split("/")[0] for n in names}

        strip = ""
        if len(tops) == 1:
            root = tops.pop()
            if all(n.startswith(root + "/") for n in names):
                strip = root + "/"

        file_members = [m for m in members if not m.filename.endswith("/")]
        total = len(file_members)
        done  = 0

        for member in members:
            rel = member.filename[len(strip):]
            if not rel:
                continue
            target = dest / rel
            if member.filename.endswith("/"):
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                tf = time.perf_counter()
                with zf.open(member) as src, open(target, "wb") as dst:
                    shutil.copyfileobj(src, dst, length=1 << 20)
                elapsed = time.perf_counter() - tf
                if elapsed > 0.5:
                    print(f"[extract]  slow file ({elapsed:.2f}s)  {rel}")
                done += 1
                if progress_cb and total:
                    progress_cb(done, total)


class _DownloadWorker(QObject):
    progress = Signal(int)   # 0–100 download · 101–200 extraction
    finished = Signal(str)   # emits the version tag on success
    error    = Signal(str)   # emits an error message

    def __init__(self, tool: dict):
        super().__init__()
        self._tool = tool

    def run(self):
        folder: Path = self._tool["folder"]
        folder.mkdir(parents=True, exist_ok=True)

        zip_url = self._tool.get("zip_url", "")
        if zip_url:
            self._run_direct(folder, zip_url)
        else:
            self._run_release(folder)

    def _run_direct(self, folder: Path, url: str):
        """Download a zip directly and keep it — Blender installs addons from the zip."""
        zip_path = folder / f"{folder.name}.zip"
        self._download(url, zip_path, total_size=0)
        if zip_path.exists():
            _save_version(folder, "direct")
            self.finished.emit("direct")

    def _run_release(self, folder: Path):
        """Download from the latest GitHub release."""
        release = fetch_latest_release(self._tool["repo"])
        if release is None:
            self.error.emit("Could not reach GitHub. Check your connection.")
            return

        asset = _find_zip_asset(release)
        if not asset:
            self.error.emit("No .zip asset found in the latest release.")
            return

        zip_path = folder / asset["name"]
        self._download(asset["browser_download_url"], zip_path, asset.get("size", 0))
        if zip_path.exists():
            self._extract(zip_path, folder)
            tag = release["tag_name"]
            _save_version(folder, tag)
            self.finished.emit(tag)
            self._cleanup(zip_path)

    def _download(self, url: str, zip_path: Path, total_size: int):
        name = zip_path.name
        print(f"[download] starting  {name}  url={url}")
        t0 = time.perf_counter()
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/octet-stream"})
            with urllib.request.urlopen(req, timeout=60) as response:
                downloaded = 0
                with open(zip_path, "wb") as f:
                    while chunk := response.read(65536):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            self.progress.emit(int(downloaded / total_size * 100))
        except Exception as e:
            zip_path.unlink(missing_ok=True)
            self.error.emit(f"Download failed: {e}")
        print(f"[download] done  {time.perf_counter() - t0:.2f}s")

    def _extract(self, zip_path: Path, folder: Path):
        print(f"[extract]  starting  {zip_path.name}")
        t1 = time.perf_counter()
        try:
            _extract_flat(
                zip_path, folder,
                progress_cb=lambda done, total: self.progress.emit(100 + int(done / total * 100)),
            )
        except Exception as e:
            print(f"[extract]  ERROR — {e}")
            self.error.emit(f"Extraction failed: {e}")
            try:
                zip_path.unlink()
            except OSError:
                pass
        print(f"[extract]  done  {time.perf_counter() - t1:.2f}s")

    def _cleanup(self, zip_path: Path):
        print(f"[cleanup]  deleting  {zip_path.name}")
        t2 = time.perf_counter()
        try:
            zip_path.unlink()
            print(f"[cleanup]  done  {time.perf_counter() - t2:.2f}s")
        except OSError as e:
            print(f"[cleanup]  failed — {e}")


# ── Public Downloader ──────────────────────────────────────────────────────────

class Downloader(QObject):
    """
    Start a background download for one tool.
    Signals:
      progress(int)   — 0-100
      finished(str)   — version tag on success
      error(str)      — message on failure
    """
    progress = Signal(int)
    finished = Signal(str)
    error    = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._thread = None
        self._worker = None

    def start(self, tool: dict):
        self._thread = QThread()
        self._worker = _DownloadWorker(tool)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self.progress)
        self._worker.finished.connect(self.finished)
        self._worker.error.connect(self.error)
        self._worker.finished.connect(self._thread.quit)
        self._worker.error.connect(self._thread.quit)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.finished.connect(self.deleteLater)

        self._thread.start()
