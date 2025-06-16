import sys
import os
from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QFileDialog,
    QHBoxLayout,
    QApplication,
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import QUrl
from managers.subtitle_manager import DraggableSubtitle


def gerar_nome_arquivo_sequencial(pasta, prefixo="gravacao_final", extensao=".mp4"):
    i = 1
    while True:
        nome = f"{prefixo}_{i:03d}{extensao}"
        caminho = os.path.join(pasta, nome)
        if not os.path.exists(caminho):
            return caminho
        i += 1


class EditionWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RinoVision - Edição Final")
        self.setGeometry(100, 100, 1280, 800)
        self.setStyleSheet("background-color: #222; color: white;")

        self.video_path = None

        self.video_widget = QVideoWidget()
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setVideoOutput(self.video_widget)
        self.player.setAudioOutput(self.audio_output)

        self.load_button = QPushButton("Carregar Vídeo")
        self.load_button.clicked.connect(self.load_video)

        self.caption_button = QPushButton("Adicionar Legenda")
        self.caption_button.clicked.connect(self.add_subtitle)

        self.export_button = QPushButton("Exportar Vídeo Editado")
        self.export_button.clicked.connect(self.export_video)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.video_widget)

        controls = QHBoxLayout()
        controls.addWidget(self.load_button)
        controls.addWidget(self.caption_button)
        controls.addWidget(self.export_button)
        layout.addLayout(controls)

        self.setLayout(layout)

    def load_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Escolher Vídeo", os.getcwd(), "Vídeos (*.mp4 *.mov *.avi)"
        )
        if file_path:
            self.video_path = file_path
            self.player.setSource(QUrl.fromLocalFile(file_path))
            self.player.play()

    def add_subtitle(self):
        subtitle = DraggableSubtitle("Insira o texto da legenda", self)
        subtitle.move(100, 700)
        subtitle.show()

    def export_video(self):
        print("[TODO] Exportação de vídeo com overlays e legendas será implementada.")
        # Sugestão futura: usar ffmpeg ou moviepy para combinar vídeo com elementos


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EditionWindow()
    window.show()
    sys.exit(app.exec())
