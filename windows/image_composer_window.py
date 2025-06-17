from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtGui import QFont


class ImageComposerWindow(QWidget):
    def __init__(self, scene_manager):
        super().__init__()
        self.setWindowTitle("Image Composition Tools")
        self.setGeometry(150, 150, 400, 300)
        self.setStyleSheet("background-color: #2e2e2e; color: white;")

        self.scene_manager = scene_manager
        layout = QVBoxLayout()

        # Título
        title = QLabel("Ferramentas de Composição")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("margin-bottom: 20px;")
        layout.addWidget(title)

        # Botão para abrir Webcam
        webcam_btn = QPushButton("📷 Abrir Webcam")
        webcam_btn.clicked.connect(self.open_webcam)
        layout.addWidget(webcam_btn)

        # Botão para abrir Base
        base_btn = QPushButton("🖼️ Abrir Base")
        base_btn.clicked.connect(self.open_base)
        layout.addWidget(base_btn)

        # Botão para agrupar
        lock_btn = QPushButton("🔒 Agrupar Base + Webcam")
        lock_btn.clicked.connect(self.lock_group)
        layout.addWidget(lock_btn)

        # Botão para iniciar gravação
        rec_btn = QPushButton("🔴 Iniciar Gravação")
        rec_btn.clicked.connect(self.start_recording)
        layout.addWidget(rec_btn)

        # Botão para parar gravação
        stop_btn = QPushButton("⏹️ Parar Gravação")
        stop_btn.clicked.connect(self.stop_recording)
        layout.addWidget(stop_btn)

        self.setLayout(layout)

    def open_webcam(self):
        from windows.webcam_window import WebcamWindow
        self.webcam = WebcamWindow()
        self.webcam.show()

    def open_base(self):
        from windows.base_window import BaseWindow
        self.base = BaseWindow()
        self.base.show()

    def lock_group(self):
        self.scene_manager.lock_group(["BaseWindow", "WebcamWindow"])

    def start_recording(self):
        self.scene_manager.iniciar_gravacao()

    def stop_recording(self):
        self.scene_manager.parar_gravacao()
