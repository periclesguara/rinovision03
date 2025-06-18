from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QFont
from managers.scene_manager import SceneManager


class CompositorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RinoVision - Compositor")
        self.setGeometry(100, 100, 1400, 800)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")

        self.scene_manager = SceneManager()

        self.central_frame = QFrame()
        self.central_frame.setStyleSheet("background-color: #2c2c2c;")
        self.setCentralWidget(self.central_frame)

        self.layout = QVBoxLayout(self.central_frame)
        self.button_layout = QHBoxLayout()

        self.init_ui()

    def init_ui(self):
        self.lock_btn = self.create_button("🔒 Lock", self.lock_windows)
        self.rec_btn = self.create_button(
            "🔴 REC", self.start_recording, highlight=True
        )
        self.stop_btn = self.create_button("⏹️ Stop", self.stop_recording)
        self.fullscreen_btn = self.create_button("⛶ Tela Cheia", self.toggle_fullscreen)
        self.edit_btn = self.create_button("✏️ Editor", self.placeholder_edition)

        for btn in [
            self.lock_btn,
            self.rec_btn,
            self.stop_btn,
            self.fullscreen_btn,
            self.edit_btn,
        ]:
            self.button_layout.addWidget(btn)

        self.layout.addLayout(self.button_layout)

    def create_button(self, text, callback, highlight=False):
        btn = QPushButton(text)
        btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        base_style = """
            QPushButton {
                background-color: #333;
                border: 2px solid #00BCD4;
                border-radius: 12px;
                padding: 12px 20px;
                font-size: 16px;
                color: white;
            }
            QPushButton:hover {
                background-color: #444;
                border: 2px solid #03A9F4;
            }
        """
        rec_style = """
            QPushButton {
                background-color: #b71c1c;
                border: 2px solid #f44336;
                border-radius: 12px;
                padding: 12px 20px;
                font-size: 16px;
                color: white;
            }
            QPushButton:hover {
                background-color: #d32f2f;
                border: 2px solid #ff5252;
            }
        """
        btn.setStyleSheet(rec_style if highlight else base_style)
        btn.clicked.connect(callback)
        return btn

    def lock_windows(self):
        print("[LOCK] Agrupando Base + Webcam")
        self.scene_manager.add_object("BaseWindow")
        self.scene_manager.add_object("WebcamWindow")
        self.scene_manager.lock_group(["BaseWindow", "WebcamWindow"])

    def start_recording(self):
        self.scene_manager.iniciar_gravacao()

    def stop_recording(self):
        self.scene_manager.parar_gravacao()

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def placeholder_edition(self):
        print("[Editor] Janela de edição ainda não implementada.")


if __name__ == "__main__":
    app = QApplication([])
    compositor = CompositorWindow()
    compositor.show()
    app.exec()

    def open_webcam_window(self):
        from windows.webcam_window import WebcamWindow

        self.webcam_window = WebcamWindow()
        self.webcam_window.show()

    def open_base_window(self):
        from windows.base_window import BaseWindow

        self.base_window = BaseWindow()
        self.image_composer_window = ImageComposerWindow()
        self.base_window.show()




    def open_image_composer(self):
        if self.image_composer_window is None:
            self.image_composer_window = ImageComposerWindow(self.scene_manager)
        self.image_composer_window.show()
