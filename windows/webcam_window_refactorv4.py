import sys
try:
    from PySide6.QtCore import QTimer, Qt
    from PySide6.QtGui import QImage, QPixmap
    from PySide6.QtWidgets import QApplication, QLabel, QHBoxLayout, QPushButton, QVBoxLayout, QWidget
    _PYSIDE_IMPORT_ERROR = None
except ImportError as exc:
    QApplication = QTimer = Qt = QImage = QPixmap = QLabel = QHBoxLayout = QPushButton = QVBoxLayout = None
    QWidget = object
    _PYSIDE_IMPORT_ERROR = exc


def _load_runtime_dependencies():
    if _PYSIDE_IMPORT_ERROR:
        raise RuntimeError(f"PySide6 unavailable for WebcamWindow: {_PYSIDE_IMPORT_ERROR}") from _PYSIDE_IMPORT_ERROR
    from managers.webcam_manager_refactorv1 import WebcamManager

    return WebcamManager

class WebcamWindow(QWidget):
    def __init__(self):
        WebcamManager = _load_runtime_dependencies()
        super().__init__()
        self.setWindowTitle("RinoVision - Webcam Transparente")

        self.manager = WebcamManager()
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)

        # Botões
        self.btn_transparent = QPushButton("Transparente")
        self.btn_blur = QPushButton("Blur")
        self.btn_white = QPushButton("Branco")
        self.btn_black = QPushButton("Preto")
        self.btn_none = QPushButton("Normal")
        self.btn_moldura = QPushButton("Moldura Transparente")

        self.btn_transparent.clicked.connect(lambda: self.manager.set_effect("transparent"))
        self.btn_blur.clicked.connect(lambda: self.manager.set_effect("blur"))
        self.btn_white.clicked.connect(lambda: self.manager.set_effect("white"))
        self.btn_black.clicked.connect(lambda: self.manager.set_effect("black"))
        self.btn_none.clicked.connect(lambda: self.manager.set_effect(None))
        self.btn_moldura.clicked.connect(self.toggle_moldura)

        # Layout
        hbox = QHBoxLayout()
        for btn in [self.btn_none, self.btn_transparent, self.btn_blur, self.btn_white, self.btn_black]:
            hbox.addWidget(btn)

        vbox = QVBoxLayout()
        vbox.addWidget(self.btn_moldura)
        vbox.addWidget(self.label)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.transparent_mode = False

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        frame = self.manager.read_frame()
        if frame is None:
            return

        if frame.shape[2] == 4:
            h, w, _ = frame.shape
            img = QImage(frame.data, w, h, QImage.Format_RGBA8888)
        else:
            h, w, _ = frame.shape
            img = QImage(frame.data, w, h, 3 * w, QImage.Format_BGR888)

        pix = QPixmap.fromImage(img)
        self.label.setPixmap(pix)

    def toggle_moldura(self):
        self.transparent_mode = not self.transparent_mode
        self.setWindowOpacity(0.4 if self.transparent_mode else 1.0)

    def closeEvent(self, event):
        self.manager.release()
        event.accept()

if __name__ == "__main__":
    if _PYSIDE_IMPORT_ERROR:
        raise RuntimeError(f"PySide6 unavailable for WebcamWindow: {_PYSIDE_IMPORT_ERROR}") from _PYSIDE_IMPORT_ERROR
    app = QApplication(sys.argv)
    window = WebcamWindow()
    window.show()
    sys.exit(app.exec())
