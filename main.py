import sys
import ctypes
from pathlib import Path
from PySide6.QtWidgets import QApplication, QStackedWidget
from PySide6.QtGui import QColor, QPalette, QIcon

from game_data import GAMES
from game_select import GameSelectScreen
from main_window import MainWindow


if __name__ == "__main__":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("JasperZebra.ToolHub")
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    _base = Path(sys._MEIPASS) if getattr(sys, "frozen", False) else Path(__file__).parent
    _ico = _base / "assets" / "main_tool_icon" / "tool_hub.ico"

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(8, 10, 16))
    palette.setColor(QPalette.WindowText, QColor(220, 230, 255))
    palette.setColor(QPalette.Base, QColor(12, 14, 22))
    palette.setColor(QPalette.AlternateBase, QColor(16, 18, 28))
    palette.setColor(QPalette.Text, QColor(220, 230, 255))
    palette.setColor(QPalette.Button, QColor(20, 22, 32))
    palette.setColor(QPalette.ButtonText, QColor(220, 230, 255))
    app.setPalette(palette)

    stack = QStackedWidget()
    stack.setWindowTitle("Tool Hub")
    stack.resize(1366, 768)
    stack.setMinimumSize(1366, 768)

    for game in GAMES:
        for tool in game["tools"]:
            tool["folder"].mkdir(parents=True, exist_ok=True)

    game_select = GameSelectScreen(GAMES)
    stack.addWidget(game_select)

    def on_game_selected(game: dict):
        tool_window = MainWindow(game)
        tool_window.back_requested.connect(lambda: go_back(tool_window))
        idx = stack.addWidget(tool_window)
        stack.setCurrentIndex(idx)

    def go_back(tool_window: MainWindow):
        stack.setCurrentIndex(0)
        stack.removeWidget(tool_window)
        tool_window.deleteLater()

    game_select.game_selected.connect(on_game_selected)

    if _ico.exists():
        _qico = QIcon(str(_ico))
        app.setWindowIcon(_qico)
        stack.setWindowIcon(_qico)

    stack.show()

    sys.exit(app.exec())
