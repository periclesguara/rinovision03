import sys
from PySide6.QtWidgets import QApplication
from windows.compositor_window import CompositorWindow

def main():
    app = QApplication(sys.argv)
    window = CompositorWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
