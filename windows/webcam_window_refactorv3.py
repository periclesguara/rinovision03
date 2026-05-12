import sys
try:
    from PySide6.QtCore import QTimer
    from PySide6.QtGui import QImage, QPixmap
    from PySide6.QtWidgets import QApplication, QLabel, QHBoxLayout, QPushButton, QVBoxLayout, QWidget
    _PYSIDE_IMPORT_ERROR = None
except ImportError as exc:
    QApplication = QTimer = QImage = QPixmap = QLabel = QHBoxLayout = QPushButton = QVBoxLayout = None
    QWidget = object
    _PYSIDE_IMPORT_ERROR = exc


def _load_runtime_dependencies():
    if _PYSIDE_IMPORT_ERROR:
        raise RuntimeError(f"PySide6 unavailable for WebcamWindow: {_PYSIDE_IMPORT_ERROR}") from _PYSIDE_IMPORT_ERROR
    from managers.webcam_manager import WebcamManager

    return WebcamManager


class WebcamWindow(QWidget):
    def __init__(self):
        WebcamManager = _load_runtime_dependencies()
        super().__init__()
        self.setWindowTitle("Webcam com Efeitos e Transparência")
        self.setGeometry(200, 200, 800, 600)

        self.manager = WebcamManager()

        # Layouts
        main_layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        # Label para exibir vídeo
        self.label = QLabel()
        self.label.setFixedSize(640, 480)
        main_layout.addWidget(self.label)

        # Botões de efeito
        self.btn_transparent = QPushButton("Transparente")
        self.btn_blur = QPushButton("Blur")
        self.btn_black = QPushButton("Fundo Preto")
        self.btn_white = QPushButton("Fundo Branco")

        # Conectar botões
        self.btn_transparent.clicked.connect(lambda: self.manager.set_effect("transparent"))
        self.btn_blur.clicked.connect(lambda: self.manager.set_effect("blur"))
        self.btn_black.clicked.connect(lambda: self.manager.set_effect("black"))
        self.btn_white.clicked.connect(lambda: self.manager.set_effect("white"))

        # Adicionar botões ao layout
        button_layout.addWidget(self.btn_transparent)
        button_layout.addWidget(self.btn_blur)
        button_layout.addWidget(self.btn_black)
        button_layout.addWidget(self.btn_white)

        main_layout.addLayout(button_layout)

        # Timer para capturar frames
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 30 ms ~ 33 FPS

        self.setLayout(main_layout)

    def update_frame(self):
        frame = self.manager.get_frame()
        if frame is not None:
            if frame.shape[2] == 4:
                qimg = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGBA8888)
            else:
                qimg = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_BGR888)
            self.label.setPixmap(QPixmap.fromImage(qimg))

    def closeEvent(self, event):
        self.manager.release()
        event.accept()


if __name__ == '__main__':
    if _PYSIDE_IMPORT_ERROR:
        raise RuntimeError(f"PySide6 unavailable for WebcamWindow: {_PYSIDE_IMPORT_ERROR}") from _PYSIDE_IMPORT_ERROR
    app = QApplication(sys.argv)
    window = WebcamWindow()
    window.show()
    sys.exit(app.exec())
