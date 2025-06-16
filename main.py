import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from utils.logger import setup_logger

logger = setup_logger()
logger.info("🚀 RinoVision iniciado com sucesso!")

from PySide6.QtWidgets import QApplication
from windows.compositor_window import CompositorWindow

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = CompositorWindow()
    window.show()
    sys.exit(app.exec())
