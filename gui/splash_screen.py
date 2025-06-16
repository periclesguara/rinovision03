from PySide6.QtWidgets import QSplashScreen, QLabel, QProgressBar
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import Qt, QTimer


class SplashScreen(QSplashScreen):
    def __init__(self, image_path="assets/splash.png"):
        pixmap = QPixmap(image_path)
        super().__init__(pixmap)

        self.setWindowFlag(Qt.FramelessWindowHint)  # Remove bordas
        self.setWindowFlag(Qt.WindowStaysOnTopHint)  # Sempre no topo
        self.setMask(pixmap.mask())  # Máscara da imagem

        # Texto de status
        self.status = QLabel(self)
        self.status.setGeometry(10, pixmap.height() - 60, pixmap.width() - 20, 20)
        self.status.setStyleSheet("color: white; font-size: 14px;")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setText("Inicializando...")

        # Barra de progresso
        self.progress = QProgressBar(self)
        self.progress.setGeometry(10, pixmap.height() - 30, pixmap.width() - 20, 20)
        self.progress.setStyleSheet(
            """
            QProgressBar {
                background-color: #333;
                color: white;
                border: 1px solid white;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #05B8CC;
                width: 20px;
            }
        """
        )
        self.progress.setValue(0)

    def update_message(self, message, progress_value):
        """Atualiza texto e barra de progresso."""
        self.status.setText(message)
        self.progress.setValue(progress_value)
