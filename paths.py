import sys
from pathlib import Path

# cx_Freeze: .py files live in lib/ but assets live in the exe's parent folder.
# Dev: everything is in the same directory as this file.
if getattr(sys, "frozen", False):
    ASSET_ROOT = Path(sys.executable).parent
else:
    ASSET_ROOT = Path(__file__).parent
