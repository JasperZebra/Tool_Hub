import sys
from pathlib import Path
from PySide6.QtGui import QColor

# Root folder where all tool installations live.
# When frozen (PyInstaller), use the exe's directory so tools always
# install next to the launcher, not inside a temporary extraction dir.
_BASE = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent
TOOLS_DIR = _BASE / "tools"

# Shorthand helpers
ATG  = TOOLS_DIR / "avatar_and_fc2"
AFOP = TOOLS_DIR / "afop"
# FC2 shares the same tool binaries as ATG — no separate folder

GAMES = [
    {
        "name": "Avatar: The Game",
        "short": "ATG '09",
        "tag": "DUNIA ENGINE · 2009",
        "desc": "Modding tools for Ubisoft's 2009 Avatar film tie-in game.",
        "accent": QColor(0, 180, 255),
        "icon_char": "⬡",
        "tools": [
            {
                "name": "Save Editor",
                "tag": "X360 / PC",
                "desc": "Cross-platform save editor for the 2009 Avatar game. Supports PS3, Xbox 360, and PC save files with full field editing and PS3 PADDING.000 preservation.",
                "accent": QColor(0, 180, 255),
                "icon_char": "◉",
                "stats": [("By", "JasperZebra"), ("X360/PC", "✓")],
                "folder": ATG / "save_editor",
                "repo": "JasperZebra/AVATAR-Save-Editor",
                "exe": "AVATAR_The_Game_Save_Editor_V2.2.exe",  # fill in after download
            },
            {
                "name": "Level Editor",
                "tag": "DUNIA ENGINE",
                "desc": "GUI-based level editor for Avatar: The Game. Edit entity placement, trigger zones, and world data stored in the Dunia FCB format.",
                "accent": QColor(0, 200, 220),
                "icon_char": "◈",
                "stats": [("By", "JasperZebra"), ("Format", ".fcb"), ("Platform", "PC")],
                "folder": ATG / "level_editor",
                "repo": "JasperZebra/AVATAR-The-Game-Level-Editor",
                "exe": "Avatar_Level_Editor.exe",  # fill in after download
            },
            {
                "name": "File Editor",
                "tag": "DUNIA ENGINE",
                "desc": "General-purpose file editor for Dunia engine resources. Browse, inspect, and modify raw game data files with hex and structured views.",
                "accent": QColor(0, 160, 240),
                "icon_char": "◉",
                "stats": [("By", "JasperZebra"), ("Engine", "Dunia"), ("Platform", "PC")],
                "folder": ATG / "file_editor",
                "repo": "JasperZebra/AVATAR-.game.xml-File-Editor",
                "exe": "AVATAR_XML_File_Editor.exe",  # fill in after download
            },
            {
                "name": "Mod Manager",
                "tag": "ATG MODDING",
                "desc": "Manage and load PAK-based mods for Avatar: The Game. Enable, disable, and organize mods with conflict detection and load order control.",
                "accent": QColor(80, 200, 255),
                "icon_char": "⬡",
                "stats": [("By", "JasperZebra"), ("Format", ".pak"), ("Platform", "PC")],
                "folder": ATG / "mod_manager",
                "repo": "JasperZebra/AVATAR-_The_Game_Mod_Manager",
                "exe": "Avatar_Mod_Manager.exe",
            },
            {
                "name": "XBT ↔ DDS Converter",
                "tag": "TEXTURE TOOL",
                "desc": "Convert between the game's native XBT texture format and standard DDS. Round-trip safe with full header and mipmap preservation.",
                "accent": QColor(0, 220, 255),
                "icon_char": "◈",
                "stats": [("By", "JasperZebra"), ("Input", ".xbt"), ("Output", ".dds")],
                "folder": ATG / "xbt_dds_converter",
                "repo": "JasperZebra/AVATAR_XBT_to_DDS_Converter",
                "exe": "XBT_DDS_Converter.exe",  # drag-and-drop tool — opens folder
            },
            {
                "name": "XBM Color Editor",
                "tag": "MATERIAL TOOL",
                "desc": "Edit color values embedded in XBM material files. Visual color picker with hex and RGBA support for direct material customization.",
                "accent": QColor(0, 200, 200),
                "icon_char": "◉",
                "stats": [("By", "JasperZebra"), ("Format", ".xbm"), ("Type", "Color")],
                "folder": ATG / "xbm_color_editor",
                "repo": "JasperZebra/AVATAR_XBM_Color_Editor",
                "exe": "XBM_Color_Editor.exe",  # fill in after download
            },
            {
                "name": "PAK Unpacker & Repacker",
                "tag": "ARCHIVE TOOL",
                "desc": "Extract game assets from PAK archives and repack modified files back in. Full round-trip editing with path and metadata preservation.",
                "accent": QColor(0, 140, 220),
                "icon_char": "⬡",
                "stats": [("By", "JasperZebra"), ("Format", ".pak"), ("Mode", "R / W")],
                "folder": ATG / "pak_unpacker_repacker",
                "repo": "JasperZebra/AVATAR_The_Game_Unpacker_and_Repacker",
                "exe": "",  # drag-and-drop tool — opens folder
            },
            {
                "name": "XBM Material Viewer",
                "tag": "MATERIAL TOOL",
                "desc": "View and inspect XBM material definitions and their shader parameters. Read-only viewer with structured property display and export.",
                "accent": QColor(60, 190, 210),
                "icon_char": "◉",
                "stats": [("By", "Quiet Joker"), ("Format", ".xbm"), ("Type", "Viewer")],
                "folder": ATG / "xbm_material_viewer",
                "repo": "",
                "exe": "",
                "coming_soon": True,
            },
            {
                "name": "XBG Blender Addon",
                "tag": "BLENDER ADD-ON",
                "desc": "Blender add-on for importing and exporting XBG mesh files from Avatar: The Game. Supports rigged meshes with full bone weight transfer.",
                "accent": QColor(0, 210, 180),
                "icon_char": "◈",
                "stats": [("By", "Quiet Joker"), ("App", "Blender"), ("Format", ".xbg")],
                "folder": ATG / "xbg_blender_addon",
                "repo": "",
                "zip_url": "https://github.com/Quiet-Joker/Avatar-XBG-Blender-Importer/archive/refs/heads/main.zip",
                "exe": "",  # Blender addon — opens folder
            },
            {
                "name": "Heightmap Viewer",
                "tag": "TERRAIN TOOL",
                "desc": "Visualize terrain heightmap data from Avatar: The Game in real time with color-mapped elevation display and export to image formats.",
                "accent": QColor(40, 180, 200),
                "icon_char": "◉",
                "stats": [("By", "Quiet Joker"), ("Type", "Viewer"), ("Format", "HMP")],
                "folder": ATG / "heightmap_viewer",
                "repo": "",
                "exe": "",
                "coming_soon": True,
            },
            {
                "name": "Blender Terrain Editor",
                "tag": "BLENDER ADD-ON",
                "desc": "Edit Avatar: The Game terrain meshes directly inside Blender. Import, modify, and re-export terrain chunks with height and texture data.",
                "accent": QColor(80, 220, 200),
                "icon_char": "◈",
                "stats": [("By", "Quiet Joker"), ("App", "Blender"), ("Type", "Terrain")],
                "folder": ATG / "blender_terrain_editor",
                "repo": "",
                "zip_url": "https://github.com/Quiet-Joker/Avatar-Blender-Terrain-Editor/archive/refs/heads/main.zip",
                "exe": "",  # Blender addon — opens folder
            },
            {
                "name": "XBG Extractor",
                "tag": "MESH TOOL",
                "desc": "Extract XBG mesh files from Avatar: The Game archives for modding or inspection. Batch extraction supported with path reconstruction.",
                "accent": QColor(0, 120, 200),
                "icon_char": "⬡",
                "stats": [("By", "FDX4061"), ("Format", ".xbg"), ("Mode", "Extract")],
                "folder": ATG / "xbg_extractor",
                "repo": "fdx4061/EXTRACTOR-xbg-resources-avatar-fc234",
                "exe": "",
            },
            {
                "name": "XBM Editor",
                "tag": "MATERIAL TOOL",
                "desc": "Edit XBM material files for Avatar: The Game and Far Cry 2. Modify shader parameters, texture references, and material properties.",
                "accent": QColor(0, 100, 180),
                "icon_char": "◉",
                "stats": [("By", "FDX4061"), ("Format", ".xbm"), ("Mode", "Edit")],
                "folder": ATG / "xbm_editor",
                "repo": "fdx4061/xbmEditor-by-fdx",
                "exe": "xbmEditor.exe",
            },
        ],
    },
    {
        "name": "Far Cry 2",
        "short": "FC2",
        "tag": "DUNIA ENGINE · 2008",
        "desc": "Modding tools for Ubisoft's Far Cry 2.",
        "accent": QColor(255, 140, 0),
        "icon_char": "◈",
        "tools": [
            {
                "name": "Level Editor",
                "tag": "DUNIA ENGINE",
                "desc": "GUI-based level editor for Far Cry 2. Edit entity placement, trigger zones, and world data stored in the Dunia FCB format.",
                "accent": QColor(255, 140, 0),
                "icon_char": "◈",
                "stats": [("By", "JasperZebra"), ("Format", ".fcb"), ("Platform", "PC")],
                "folder": ATG / "level_editor",
                "repo": "JasperZebra/AVATAR-The-Game-Level-Editor",
                "exe": "Avatar_Level_Editor.exe",  # fill in after download
            },
            {
                "name": "XBT ↔ DDS Converter",
                "tag": "TEXTURE TOOL",
                "desc": "Convert between Far Cry 2's native XBT texture format and standard DDS. Round-trip safe with full header and mipmap preservation.",
                "accent": QColor(255, 165, 30),
                "icon_char": "◈",
                "stats": [("By", "JasperZebra"), ("Input", ".xbt"), ("Output", ".dds")],
                "folder": ATG / "xbt_dds_converter",
                "repo": "JasperZebra/AVATAR_XBT_to_DDS_Converter",
                "exe": "XBT_DDS_Converter.exe",  # drag-and-drop tool — opens folder
            },
            {
                "name": "XBG Blender Addon",
                "tag": "BLENDER ADD-ON",
                "desc": "Blender add-on for importing and exporting XBG mesh files from Far Cry 2. Supports rigged meshes with full bone weight transfer.",
                "accent": QColor(255, 185, 60),
                "icon_char": "◈",
                "stats": [("By", "Quiet Joker"), ("App", "Blender"), ("Format", ".xbg")],
                "folder": ATG / "xbg_blender_addon",
                "repo": "",
                "zip_url": "https://github.com/Quiet-Joker/Avatar-XBG-Blender-Importer/archive/refs/heads/main.zip",
                "exe": "",  # Blender addon — opens folder
            },
            {
                "name": "XBG Extractor",
                "tag": "MESH TOOL",
                "desc": "Extract XBG mesh files from Far Cry 2 archives for modding or inspection. Batch extraction supported with path reconstruction.",
                "accent": QColor(220, 110, 0),
                "icon_char": "⬡",
                "stats": [("By", "FDX4061"), ("Format", ".xbg"), ("Mode", "Extract")],
                "folder": ATG / "xbg_extractor",
                "repo": "fdx4061/EXTRACTOR-xbg-resources-avatar-fc234",
                "exe": "",
            },
            {
                "name": "XBM Editor",
                "tag": "MATERIAL TOOL",
                "desc": "Edit XBM material files for Far Cry 2. Modify shader parameters, texture references, and material properties.",
                "accent": QColor(200, 90, 0),
                "icon_char": "◉",
                "stats": [("By", "FDX4061"), ("Format", ".xbm"), ("Mode", "Edit")],
                "folder": ATG / "xbm_editor",
                "repo": "fdx4061/xbmEditor-by-fdx",
                "exe": "xbmEditor.exe",
            },
        ],
    },
    {
        "name": "Avatar: Frontiers of Pandora",
        "short": "AFoP",
        "tag": "SNOWDROP ENGINE · 2023",
        "desc": "Modding tools for Massive Entertainment's Avatar: Frontiers of Pandora.",
        "accent": QColor(0, 255, 140),
        "icon_char": "◉",
        "tools": [
            {
                "name": "AFoP Mesh Tool",
                "tag": "BLENDER ADD-ON",
                "desc": "Blender add-on for editing .mmb mesh files in Avatar: Frontiers of Pandora. Supports mesh versions 12–17 with full vertex and bone weight control.",
                "accent": QColor(0, 255, 140),
                "icon_char": "◈",
                "stats": [("By", "JZ / KW / SB"), ("Format", ".mmb"), ("Versions", "12–17")],
                "folder": AFOP / "afop_mesh_tool",
                "repo": "",
                "zip_url": "https://github.com/J-Lyt/AFoPMeshTool/archive/refs/heads/master.zip",
                "exe": "",  # Blender addon — opens folder
            },
            {
                "name": "Snowdrop LocPack Converter",
                "tag": "LOCALIZATION TOOL",
                "desc": "Convert Snowdrop engine .locpack localization files to and from editable formats for subtitle and UI text modding.",
                "accent": QColor(0, 220, 120),
                "icon_char": "◉",
                "stats": [("By", "Kicking Writer"), ("Format", ".locpack"), ("Type", "Convert")],
                "folder": AFOP / "snowdrop_locpack_converter",
                "repo": "JasperZebra/Snowdrop_LocPack_Converter",
                "exe": "AFOP_LocPack_Converter.exe",  # fill in after download
            },
            {
                "name": "Snowdrop Juice Converter",
                "tag": "ASSET TOOL",
                "desc": "Convert Snowdrop .juice asset bundle files for inspection and content replacement in Avatar: Frontiers of Pandora.",
                "accent": QColor(0, 200, 100),
                "icon_char": "⬡",
                "stats": [("By", "Kicking Writer"), ("Format", ".juice"), ("Type", "Convert")],
                "folder": AFOP / "snowdrop_juice_converter",
                "repo": "JasperZebra/Snowdrop_Juice_Converter",
                "exe": "AFOP_Juice_Converter.exe",  # fill in after download
            },
            {
                "name": "AFoP Texture Redirector",
                "tag": "TEXTURE TOOL",
                "desc": "Redirect AFoP texture lookups to custom files, enabling seamless texture replacement without repacking game archives.",
                "accent": QColor(60, 255, 160),
                "icon_char": "◈",
                "stats": [("By", "JasperZebra"), ("Type", "Redirect"), ("Format", ".tex")],
                "folder": AFOP / "afop_texture_redirector",
                "repo": "JasperZebra/AFoP_Texture_Redirector_Tool",
                "exe": "Texture_Redirector.exe",  # fill in after download
            },
            {
                "name": "AFoP mgraphobject Swapper",
                "tag": "ASSET TOOL",
                "desc": "Swap mgraphobject references in AFoP to replace in-game meshes and prop assets without modifying core game files.",
                "accent": QColor(0, 240, 130),
                "icon_char": "◉",
                "stats": [("By", "JasperZebra"), ("Type", "Swap"), ("Format", ".mgraph")],
                "folder": AFOP / "afop_mgraphobject_swapper",
                "repo": "JasperZebra/AFoP_mgraphobject_Swapper",
                "exe": "AFOP_Gear_Swapper.exe",  # fill in after download
            },
            {
                "name": "AFoP CamoColorPalette Editor",
                "tag": "COLOR EDITOR",
                "desc": "Edit camouflage color palette values in AFoP to fully customize camo patterns and color slot assignments.",
                "accent": QColor(200, 80, 255),
                "icon_char": "◉",
                "stats": [("By", "JasperZebra"), ("Type", "Color"), ("Target", "Camo")],
                "folder": AFOP / "afop_camocolorpalette_editor",
                "repo": "JasperZebra/AFoP_CamoColorPalette_Editor",
                "exe": "AFOP_Palette_Editor.exe",  # fill in after download
            },
            {
                "name": "AFoP Banshee Skin Color Editor",
                "tag": "COLOR EDITOR",
                "desc": "Edit Banshee (Ikran) creature skin color values in AFoP to create fully custom Ikran appearances.",
                "accent": QColor(220, 100, 255),
                "icon_char": "◉",
                "stats": [("By", "JasperZebra"), ("Type", "Color"), ("Target", "Banshee")],
                "folder": AFOP / "afop_banshee_skin_color_editor",
                "repo": "JasperZebra/AFoP-Banshee-Skin-Color-Editor",
                "exe": "AFOP_Banshee_Color_Editor.exe",
            },
            {
                "name": "AFoP Eye Color Editor",
                "tag": "COLOR EDITOR",
                "desc": "Edit Na'vi and creature eye color values in AFoP for fully custom character eye appearances.",
                "accent": QColor(180, 60, 240),
                "icon_char": "◉",
                "stats": [("By", "JasperZebra"), ("Type", "Color"), ("Target", "Eyes")],
                "folder": AFOP / "afop_eye_color_editor",
                "repo": "JasperZebra/AFoP-Eye-Color-Editor",
                "exe": "AFOP_Eye_Color_Editor.exe",
            },
            {
                "name": "AFoP Hair Color Editor",
                "tag": "COLOR EDITOR",
                "desc": "Edit Na'vi hair color values in AFoP for custom character hair appearances and highlight colors.",
                "accent": QColor(210, 90, 255),
                "icon_char": "◉",
                "stats": [("By", "JasperZebra"), ("Type", "Color"), ("Target", "Hair")],
                "folder": AFOP / "afop_hair_color_editor",
                "repo": "JasperZebra/AFoP-Hair-Color-Editor",
                "exe": "AFOP_Hair_Color_Editor.exe",
            },
            {
                "name": "AFoP Skin Color Editor",
                "tag": "COLOR EDITOR",
                "desc": "Edit Na'vi skin color values in AFoP for fully custom character skin tones and bioluminescent patterns.",
                "accent": QColor(190, 70, 245),
                "icon_char": "◉",
                "stats": [("By", "JasperZebra"), ("Type", "Color"), ("Target", "Skin")],
                "folder": AFOP / "afop_skin_color_editor",
                "repo": "JasperZebra/AFoP-Skin-Color-Editor",
                "exe": "AFOP_Skin_Color_Editor.exe",
            },
            {
                "name": "AFoP Warpaint Color Editor",
                "tag": "COLOR EDITOR",
                "desc": "Edit Na'vi warpaint color values in AFoP for custom warpaint designs, pattern colors, and overlay intensities.",
                "accent": QColor(215, 95, 250),
                "icon_char": "◉",
                "stats": [("By", "JasperZebra"), ("Type", "Color"), ("Target", "Warpaint")],
                "folder": AFOP / "afop_warpaint_color_editor",
                "repo": "JasperZebra/AFoP-Warpaint-Color-Editor",
                "exe": "AFOP_Warpaint_Color_Editor.exe",
            },
        ],
    },
]

# Propagate each game's accent into its tools so cards and the sidebar
# can colour the tag badge with the game colour rather than the tool colour.
for _game in GAMES:
    for _tool in _game["tools"]:
        _tool["game_accent"] = _game["accent"]
        _tool["accent"]      = _game["accent"]
