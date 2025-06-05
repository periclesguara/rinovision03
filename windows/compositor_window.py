import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap

from windows.base_window import BaseWindow
from windows.webcam_window import WebcamWindow
from components.control_panel import ControlPanel
from managers.audio_manager import AudioManager
from managers.record_manager import RecordManager


class CompositorWindow(QWidget):
    def __init__(self):
        super().__init__()

        from utils.patch_applier import auto_patch
        auto_patch(self)

        self.setWindowTitle("RinoVision - Compositor PRO")
        self.setGeometry(100, 100, 1920, 1080)
        self.setStyleSheet("background-color: #111;")

        self.webcam_window = None
        self.base_window = None

        # Preview central
        self.preview_label = QLabel("Preview Central")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: black; color: white; font-size: 18px;")
        self.preview_label.setFixedSize(1440, 810)

        # Painel lateral
        self.control_panel = ControlPanel()
        self.control_panel.sync_clicked.connect(self.sync_audio_video)
        self.control_panel.export_clicked.connect(self.export_final_video)
        self.control_panel.caption_clicked.connect(self.show_caption)
        self.control_panel.record_clicked.connect(self.start_recording)

        # Botões principais
        self.btn_open_webcam = QPushButton("Abrir Webcam")
        self.btn_open_base = QPushButton("Abrir Base")
        self.btn_open_webcam.clicked.connect(self.open_webcam)
        self.btn_open_base.clicked.connect(self.open_base)

        self.btn_open_webcam.setStyleSheet("color: white; background-color: #444; padding: 6px; border-radius: 5px;")
        self.btn_open_base.setStyleSheet("color: white; background-color: #444; padding: 6px; border-radius: 5px;")

        button_row = QHBoxLayout()
        button_row.addWidget(self.btn_open_webcam)
        button_row.addWidget(self.btn_open_base)
        button_row.addStretch()

        # Layout principal
        main_layout = QVBoxLayout()
        middle_layout = QHBoxLayout()
        middle_layout.addWidget(self.control_panel)
        middle_layout.addWidget(self.preview_label)
        middle_layout.addStretch()

        main_layout.addLayout(button_row)
        main_layout.addLayout(middle_layout)
        self.setLayout(main_layout)

        # Timer de preview (caso queira expandir no futuro com compositing real)
        self.render_timer = QTimer()
        self.render_timer.timeout.connect(self.render_composition)
        self.render_timer.start(100)

        # Inicializar gravação
        self.audio_manager = AudioManager()
        self.record_manager = RecordManager(preview_widget=self.preview_label, audio_manager=self.audio_manager)

    def open_webcam(self):
        try:
            if self.webcam_window is None or not self.webcam_window.isVisible():
                self.webcam_window = WebcamWindow()
                self.webcam_window.setAttribute(Qt.WA_DeleteOnClose)
                self.webcam_window.destroyed.connect(self.on_webcam_closed)
                self.webcam_window.setWindowFlags(Qt.WindowStaysOnTopHint)
                self.webcam_window.show()
            else:
                self.webcam_window.showNormal()
                self.webcam_window.raise_()
                self.webcam_window.activateWindow()
        except Exception as e:
            print(f"Erro ao abrir WebcamWindow: {e}")

    def open_base(self):
        try:
            if self.base_window is None or not self.base_window.isVisible():
                self.base_window = BaseWindow()
                self.base_window.setAttribute(Qt.WA_DeleteOnClose)
                self.base_window.destroyed.connect(self.on_base_closed)
                self.base_window.setWindowFlags(Qt.Window)
                self.base_window.show()
            else:
                self.base_window.showNormal()
                self.base_window.raise_()
                self.base_window.activateWindow()

            # Regra 3: garantir ordem correta
            if self.webcam_window:
                self.webcam_window.raise_()
                self.webcam_window.activateWindow()

        except Exception as e:
            print(f"Erro ao abrir BaseWindow: {e}")

    def on_webcam_closed(self):
        self.webcam_window = None

    def on_base_closed(self):
        self.base_window = None

    def render_composition(self):
        # Aqui pode vir código futuro que renderiza a composição final das camadas
        pass

    def sync_audio_video(self):
        print("Sincronizar áudio e vídeo")

    def export_final_video(self):
        print("Exportar vídeo final")

    def show_caption(self):
        print("Exibir legenda")

    def start_recording(self):
        print("Iniciar gravação")
        if hasattr(self, 'record_manager'):
            self.record_manager.start_recording()
        else:
            print("⚠️ RecordManager não configurado.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    compositor = CompositorWindow()
    compositor.show()
    compositor.raise_()  # Regra 1: sempre por cima
    sys.exit(app.exec())
