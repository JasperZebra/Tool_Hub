# Tool Manager — Agent Reference

## What this app is

A PySide6 desktop GUI called **Tool Hub** — a premium-styled two-screen launcher for modding tools across three games. Screen 1 is a game selection screen; screen 2 is a per-game tool hub with three view modes (carousel / grid / list) and a detail sidebar. Both screens share the same dark sci-fi aesthetic with per-game accent colors.

---

## File map

Run the app with `python main.py`. All files live in the same directory.

| File | What it contains | Edit it to… |
|---|---|---|
| `game_data.py` | `GAMES` list — all game and tool metadata | Add/remove games or tools, change names, descriptions, accent colors, stats, icons |
| `anim.py` | `AnimFloat` class — animatable float via Qt property system | Add new animatable value types for future animations |
| `card.py` | `generate_card_image()` + `ToolCard` widget | Change tool card visuals: banner art, badge, text layout, reflection effect |
| `downloader.py` | GitHub API, version tracking, background download/extract worker | Change download logic, extraction behavior, version file format |
| `detail_panel.py` | `DetailPanel` sidebar widget | Change sidebar layout, button states, download/launch wiring |
| `carousel.py` | `Carousel` widget — 3D perspective card positioning, slide animation | Adjust 3D parameters, animation speed/easing, navigation logic |
| `background.py` | `Background` widget — animated scanline backdrop | Change background colors, glow pulse speed, scanline density |
| `game_select.py` | `GameCard` + `GameSelectScreen` — game selection UI | Change game card visuals, layout, hover effects, update indicator |
| `main_window.py` | `MainWindow` — tool hub screen for a selected game | Change tool hub layout, back button, header, view modes, keyboard shortcuts |
| `main.py` | App entry point — `QStackedWidget`, palette, screen wiring | Change app-level theme, window size, screen transition logic |
| `updater.py` | Auto-updater — version check + background file download | Change repo URL, bump `APP_VERSION`, add files to `_PY_FILES` / `_ASSET_FILES` |

---

## Data (game_data.py)

Single source of truth. `GAMES` is a list of game dicts. Each game dict contains its own `tools` list.

### Game dict keys

| Key | Type | Description |
|---|---|---|
| `name` | `str` | Full game name shown on game card |
| `short` | `str` | Short name used in the tool hub header (e.g. `"ATG '09"`) |
| `tag` | `str` | Engine/year badge shown on the game card (procedural fallback only) |
| `desc` | `str` | One-line description shown on the game card (procedural fallback only) |
| `accent` | `QColor` | Per-game theme color — drives background glow and card borders |
| `icon_char` | `str` | Unicode symbol drawn in the procedural banner fallback |
| `tools` | `list[dict]` | List of tool dicts for this game (empty = "COMING SOON") |

### Tool dict keys

| Key | Type | Description |
|---|---|---|
| `name` | `str` | Display name shown on tool card and sidebar |
| `tag` | `str` | Short platform/engine tag (shown on card badge) |
| `desc` | `str` | Description shown on card and sidebar |
| `accent` | `QColor` | Per-tool theme color (can differ from the game's accent) |
| `icon_char` | `str` | Unicode symbol drawn large in the card background art |
| `stats` | `list[tuple[str,str]]` | Key/value pairs shown in the sidebar stats grid |
| `folder` | `Path` | Local install path for the tool |
| `repo` | `str` | GitHub `"owner/repo"` slug for release downloads (empty string if none) |
| `exe` | `str` | Executable filename relative to `folder` — if set, button says "LAUNCH TOOL"; if empty, says "OPEN FOLDER" |
| `zip_url` | `str` | Direct URL to download a zip — used for Blender addons; zip is kept (not extracted) |
| `coming_soon` | `bool` | If `True`, button shows "COMING SOON" and is disabled |
| `game_accent` | `QColor` | Optional — overrides the game's accent for the sidebar tag badge |

### Current games and tools

**Avatar: The Game** — `ATG '09` — Cyan `#00b4ff`

| Tool | Accent | Source |
|---|---|---|
| Save Editor | Cyan `#00b4ff` | repo |
| Level Editor | Teal `#00c8dc` | repo |
| File Editor | Blue `#00a0f0` | repo |
| Mod Manager | Sky `#50c8ff` | repo |
| XBT ↔ DDS Converter | Cyan `#00dcff` | repo |
| XBM Color Editor | Teal `#00c8c8` | repo |
| PAK Unpacker & Repacker | Blue `#008cdc` | repo |
| XBM Material Viewer | Steel `#3cbed2` | coming_soon |
| XBG Blender Addon | Seafoam `#00d2b4` | zip_url |
| Heightmap Viewer | Steel `#28b4c8` | coming_soon |
| Blender Terrain Editor | Mint `#50dcc8` | zip_url |
| XBG Extractor | Navy `#0078c8` | repo (.zip) |

**Far Cry 2** — `FC2` — Orange `#ff8c00`

| Tool | Accent | Source |
|---|---|---|
| Level Editor | Orange `#ff8c00` | repo |
| XBT ↔ DDS Converter | Amber `#ffa51e` | repo |
| XBG Blender Addon | Gold `#ffb93c` | zip_url |
| XBG Extractor | Burnt `#dc6e00` | repo (.zip) |
| XBM Editor | Amber | coming_soon |

**Avatar: Frontiers of Pandora** — `AFoP` — Green `#00ff8c`

| Tool | Accent | Source |
|---|---|---|
| AFoP Mesh Tool | Green `#00ff8c` | zip_url |
| Snowdrop LocPack Converter | Green `#00dc78` | repo |
| Snowdrop Juice Converter | Green `#00c864` | repo |
| AFoP Texture Redirector | Mint `#3cffa0` | repo |
| AFoP mgraphobject Swapper | Green `#00f082` | repo |
| AFoP CamoColorPalette Editor | Purple `#c850ff` | repo |
| AFoP Banshee Skin Color Editor | Violet `#dc64ff` | repo |
| AFoP Eye Color Editor | Purple `#b43cf0` | repo |
| AFoP Hair Color Editor | Violet `#d25aff` | repo |
| AFoP Skin Color Editor | Purple `#be46f5` | repo |
| AFoP Warpaint Color Editor | Violet `#d75ffa` | repo |

---

## Assets

```
assets/
  game_icons/       PNG per game card — slug-named (e.g. atg_09.png, fc2.png, afop.png)
                    Drawn centred with 30px padding, KeepAspectRatio — DO NOT change this logic
  tool_icons/       PNG per tool card — slug-named from tool["name"]
                    Currently: afop_banshee_skin_color_editor, afop_camocolorpalette_editor,
                    afop_eye/hair/skin/warpaint_color_editor, file_editor, level_editor,
                    mod_manager, save_editor, xbg_extractor, xbm_editor
```

Game icon slugs are derived from `game["short"]` via `re.sub(r'[^a-z0-9]+', '_', short.lower()).strip('_')`.
Tool icon slugs are derived from `tool["name"]` the same way.

---

## GameCard (game_select.py)

`QWidget` — a clickable game selection card, **360 × 440 px**.

**Signals:**
- `clicked(dict)` — emitted on left click
- `hovered(dict)` — emitted on mouse enter
- `left()` — emitted on mouse leave

**Rendering (paintEvent):**
- If `assets/game_icons/<slug>.png` exists → draws it centred with 30px padding, `KeepAspectRatio`. On hover: opacity 1.0 (was 0.75), accent glow. **Do not change this path.**
- Otherwise → procedural fallback banner (gradient, grid, icon char, tag badge, name, desc)
- Both paths draw: accent border (alpha 70/160) + tool count pill

---

## GameSelectScreen (game_select.py)

Full-window game selection screen.

- **Header left:** version label (`v0.1.0`) in white 12px Consolas + update button (hidden until update found)
- **Header right:** `"{N} GAMES"` count in white 12px Consolas
- Three `GameCard` widgets centered horizontally with 40px spacing
- Default background accent: **white** `QColor(255, 255, 255)`
- Hovering a card → `bg.set_accent(game["accent"])`
- Leaving a card → `bg.set_accent(QColor(255, 255, 255))` (resets to white)
- Clicking a card emits `game_selected(dict)`
- On init: `start_check()` fires a background version check; if newer version found, update button appears

**Update button states:**
| State | Label |
|---|---|
| No update | hidden |
| Update found | `↓  UPDATE  v1.x.x` (green, enabled) |
| Downloading | `↓  UPDATING  x/26` (disabled) |
| Success | `✓  RESTART TO APPLY` (disabled) |
| Failure | `✕  UPDATE FAILED` (re-enabled for retry) |

---

## Carousel (carousel.py)

`QWidget` — **3D perspective circle** carousel. Cards are positioned on a virtual circle; the camera looks at the front of the circle. Back cards appear smaller and more transparent.

**Constants:**
```python
RADIUS      = 900   # virtual circle radius — bigger = more depth
ANGLE_STEP  = 44    # degrees between cards (4 × 44 = 176° — stays under 180° so order never flips)
FOCAL       = 360   # perspective focal length — smaller = more dramatic size difference
MAX_VISIBLE = 4     # cards shown per side
```

**`_params(idx)`** — returns `(screen_cx, card_y, scale, opacity, z)` for a card at index `idx` given the current float position `_pos`.

**Animation:** `carousel_pos` is a `Property(float)` animated by `QPropertyAnimation` (380ms, OutCubic). Cards are sorted back→front by `z` so rear cards paint first.

**Face cache:** `_face_cache` dict keyed by index — renders card face once, reuses pixmap.

**Hard cap:** cards at `abs(diff) * ANGLE_STEP >= 179°` are skipped to prevent wrap-around rendering.

---

## DetailPanel (detail_panel.py)

Fixed-width (260px) sidebar showing the currently selected tool's details.

**Button states:**
| State | Label | Enabled |
|---|---|---|
| `coming_soon` | `⧗  COMING SOON` | No |
| Not installed | `⬇  DOWNLOAD TOOL` | Yes |
| Connecting | `⬇  CONNECTING...` | No |
| Downloading | `⬇  DOWNLOADING  N%` | No |
| Extracting | `⬇  EXTRACTING  N%` | No |
| Download failed | `✕  DOWNLOAD FAILED` | Yes (retry) |
| Installed, has exe | `▶  LAUNCH TOOL` | Yes |
| Installed, no exe | `⊞  OPEN FOLDER` | Yes |

**Download guard:** a tool needs `repo` OR `zip_url` to be downloadable. `coming_soon` blocks download regardless.

**Multi-tool tracking:** `_downloads` dict keyed by `folder` Path — survives switching between tools; switching back to a downloading tool restores the progress state.

---

## Downloader (downloader.py)

Handles GitHub release fetching, background downloading, zip extraction, and version tracking. **Only `.zip` is supported** — `.7z` support was removed.

### Zip extraction

`_extract_flat(zip_path, dest, progress_cb)` — extracts into `dest`, stripping a single top-level directory if the entire archive lives under one root folder (common on GitHub releases). Strip logic only triggers when **every** entry starts with `root/` — a single root-level file does not falsely trigger stripping.

### Direct zip_url downloads (Blender addons)

If `tool["zip_url"]` is set, the zip is downloaded to `folder/<folder_name>.zip` and **kept as-is** — not extracted. Blender installs addons from the zip file directly. Version is written as `"direct"`.

### Version helpers

- `get_installed_version(folder)` → reads `folder/version.json`, returns `"tag"` or `None`
- `_save_version(folder, tag)` → writes `{"tag": tag}`

### Status check

`check_status(tool)` → `tuple[str, dict | None]`

| Status | Meaning |
|---|---|
| `"no_repo"` | No repo or zip_url — launch-only |
| `"api_error"` | GitHub unreachable |
| `"not_installed"` | Not installed; release dict returned |
| `"up_to_date"` | Installed matches latest |
| `"update_available"` | Installed but outdated; release dict returned |

### `_is_installed(tool)`

Returns `True` if `tool["folder"]` exists and contains any file other than `version.json`.

---

## MainWindow (main_window.py)

Tool hub screen for a single selected game.

- **Header left:** `← GAMES` back button — white text, hover shifts to game accent color
- **Header center-left:** `game["short"].upper()` — white, 12px Consolas bold
- **Header right:** `"{N} TOOLS"` count — white, 12px Consolas; then three view toggle buttons
- Emits `back_requested` on back button press
- `←` / `→` keyboard shortcuts navigate the carousel

### Three view modes

Toggle buttons `⊙` `⊞` `☰` in the header. Active button uses game accent color; inactive buttons use the same grey as the back button.

| Mode | Widget | Notes |
|---|---|---|
| Carousel (0) | `Carousel` + nav dots + `◀` `▶` buttons | 3D perspective, keyboard nav |
| Grid (1) | `QScrollArea` → `QGridLayout` of `_GridCard` | 5 columns, equal stretch, vertical scroll only |
| List (2) | `QScrollArea` → `QVBoxLayout` of `_ListRow` | Full-width rows, vertical scroll only |

All three views share `_on_tool_changed(tool)` which updates: background accent, detail panel, carousel dots, all grid card selections, all list row selections simultaneously.

**`_GridCard`** — `QFrame`, `setFixedHeight(250)`, `setSizePolicy(Expanding, Fixed)`. Shows icon (100×100 or icon_char fallback), tag badge, name, install status.

**`_ListRow`** — `QFrame`, `setFixedHeight(90)`, `setSizePolicy(Expanding, Fixed)`. Shows icon (62×62), name, tag+desc inline, install status right-aligned.

Both scroll containers use `setSizePolicy(Expanding, Preferred)` + `setWidgetResizable(True)` + `ScrollBarAlwaysOff` horizontally to prevent overflow behind the detail panel.

Tool icons loaded from `assets/tool_icons/<slug>.png`; fall back to `icon_char` unicode glyph.

---

## Updater (updater.py)

Auto-updater for the launcher itself. Only touches launcher files — never anything under `tools/`.

**`APP_VERSION = (0, 1, 0)`** — bump this tuple each release.

**`_RAW_BASE`** — `https://raw.githubusercontent.com/JasperZebra/Tool_Hub/main/`

**`_PY_FILES`** — 11 launcher `.py` files.

**`_ASSET_FILES`** — 15 PNGs in `assets/game_icons/` and `assets/tool_icons/`. Add new entries here when new icons are pushed.

**`_ALL_FILES = _PY_FILES + _ASSET_FILES`** — everything downloaded on update (26 files total).

**Version check:** `_fetch_remote_version()` fetches `updater.py` from the remote repo and parses `APP_VERSION` out of it — same pattern as the XBG Blender addon.

**Workers:**
- `_CheckWorker(QObject)` — background version check; emits `finished(status, remote_ver)`
- `_ApplyWorker(QObject)` — background download; emits `progress(done, total)` and `finished(failed_list)`. Creates parent directories for assets automatically.

**Public API:**
- `start_check(on_result) → QThread`
- `start_apply(on_progress, on_finished) → QThread`
- `fmt_version(v: tuple) → str`

**Adding a new asset:** push PNG to repo → add path to `_ASSET_FILES` → bump `APP_VERSION` → push `updater.py`.

---

## Background (background.py)

Full-window backdrop widget repainted every 50ms (20 fps). Shared by both screens.

**Layers:**
1. Solid `#080a10` fill
2. Animated radial glow — radius pulses via `sin(tick * 0.04)`, alpha 30
3. Horizontal scanlines every 3px, white alpha 4
4. Top edge accent gradient line, alpha 80

**`set_accent(color)`** — called on game/tool hover or selection change.

---

## Entry point (main.py)

Creates `QApplication` with Fusion style and a dark `QPalette`, then builds a `QStackedWidget`. Default and minimum window size: **1366 × 768** (freely resizable above that).

- **Page 0** — `GameSelectScreen` (always present)
- **Page 1+** — `MainWindow` created fresh on each game selection, destroyed on back

```
game_select.game_selected → on_game_selected(game)
    → creates MainWindow(game)
    → MainWindow.back_requested → go_back()
        → removes and deletes MainWindow, returns to page 0
```

---

## Dependency graph

```
main.py
  ├─ GameSelectScreen (game_select.py)
  │    ├─ GameCard (game_select.py)
  │    ├─ Background (background.py)
  │    ├─ GAMES (game_data.py)
  │    └─ updater.py (version check on init)
  └─ MainWindow (main_window.py)
       ├─ Background (background.py)
       ├─ Carousel (carousel.py)
       │    └─ ToolCard (card.py)
       │         └─ generate_card_image (card.py)
       ├─ DetailPanel (detail_panel.py)
       │    └─ Downloader (downloader.py)
       └─ game["tools"] from GAMES (game_data.py)
```

---

## Known TODOs / gaps

- `check_status()` update-available flow not yet shown in the UI — function exists but no "UPDATE AVAILABLE" button state in DetailPanel
- `AnimFloat` (anim.py) is defined but not currently wired
- No transition animation between game select and tool hub screens
- No swipe/drag support on carousel — keyboard arrows and nav buttons only
- No keyboard shortcut to close/quit
- Tool icon PNGs missing for most ATG/FC2 tools — add to `assets/tool_icons/` and `_ASSET_FILES`
