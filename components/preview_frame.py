from PySide6.QtWidgets import QFrame, QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class PreviewFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Configuração do tamanho padrão
        self.setFixedSize(1440, 810)
        self.setStyleSheet("background-color: white; border: 3px dashed red;")

        # Área onde o conteúdo (composição) aparece
        self.preview_label = QLabel(self)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setGeometry(0, 0, 1440, 810)

        # Área da legenda (fixa na parte inferior)
        self.caption_label = QLabel(self)
        self.caption_label.setText("")
        self.caption_label.setStyleSheet(
            "font-size: 24px; color: black; background-color: rgba(255, 255, 255, 200);"
        )
        self.caption_label.setGeometry(0, 770, 1440, 40)
        self.caption_label.setAlignment(Qt.AlignCenter)

    def setPixmap(self, pixmap: QPixmap):
        """Atualiza o conteúdo do preview (imagem final composta)."""
        self.preview_label.setPixmap(pixmap)

    def set_caption(self, text: str):
        """Atualiza o texto da legenda."""
        self.caption_label.setText(text)

    def clear_caption(self):
        """Remove a legenda da tela."""
        self.caption_label.setText("")
