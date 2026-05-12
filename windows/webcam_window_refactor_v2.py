try:
    from PySide6.QtCore import QTimer, Qt
    from PySide6.QtGui import QImage, QPixmap
    from PySide6.QtWidgets import QLabel, QHBoxLayout, QPushButton, QSizePolicy, QVBoxLayout, QWidget
    _PYSIDE_IMPORT_ERROR = None
except ImportError as exc:
    QTimer = Qt = QImage = QPixmap = QLabel = QHBoxLayout = QPushButton = QSizePolicy = QVBoxLayout = None
    QWidget = object
    _PYSIDE_IMPORT_ERROR = exc


def _load_runtime_dependencies():
    if _PYSIDE_IMPORT_ERROR:
        raise RuntimeError(f"PySide6 unavailable for WebcamWindow: {_PYSIDE_IMPORT_ERROR}") from _PYSIDE_IMPORT_ERROR
    import cv2
    from managers.webcam_manager import WebcamManager

    return cv2, WebcamManager

class WebcamWindow(QWidget):
    def __init__(self):
        cv2, WebcamManager = _load_runtime_dependencies()
        super().__init__()
        self.cv2 = cv2
        self.setWindowTitle("Webcam Virtual com Segmentação")
        self.webcam = WebcamManager()
        self.effect = "blur"
        self.transparent_frame = False

        # Layout principal
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        # Label da webcam
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(self.video_label)

        # Botão de controle da moldura (transparente ou visível)
        self.toggle_frame_button = QPushButton("Moldura: ON")
        self.toggle_frame_button.clicked.connect(self.toggle_frame_transparency)
        self.layout.addWidget(self.toggle_frame_button)

        # Botões de efeitos visuais
        self.buttons_layout = QHBoxLayout()
        self.layout.addLayout(self.buttons_layout)

        for name in ["Transparente", "Preto", "Branco", "Blur"]:
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, n=name.lower(): self.set_effect(n))
            self.buttons_layout.addWidget(btn)

        # Timer de atualização
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def toggle_frame_transparency(self):
        self.transparent_frame = not self.transparent_frame
        self.toggle_frame_button.setText("Moldura: OFF" if self.transparent_frame else "Moldura: ON")
        self.setAttribute(Qt.WA_TranslucentBackground, self.transparent_frame)

    def set_effect(self, effect_name):
        self.effect = effect_name
        self.webcam.set_effect(effect_name)

    def update_frame(self):
        frame = self.webcam.get_frame()
        if frame is None:
            return

        # Conversão de cor
        if frame.shape[2] == 4:
            frame = frame[:, :, :3]

        frame = self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pix = QPixmap.fromImage(image).scaled(
            self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.video_label.setPixmap(pix)

    def resizeEvent(self, event):
        self.update_frame()
        return super().resizeEvent(event)

    def closeEvent(self, event):
        self.webcam.release()
        super().closeEvent(event)

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    win = WebcamWindow()
    win.show()
    sys.exit(app.exec())
