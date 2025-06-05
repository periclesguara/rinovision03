from PySide6.QtWidgets import (
    QWidget, QPushButton, QLabel, QVBoxLayout
)
from PySide6.QtCore import Qt, Signal


class ControlPanel(QWidget):
    sync_clicked = Signal()
    export_clicked = Signal()
    caption_clicked = Signal()
    record_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedSize(220, 400)
        self.setStyleSheet("background-color: #333; border: 2px solid #888; border-radius: 8px;")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        # Título
        title_label = QLabel("Painel de Controle")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 16px;")
        title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title_label)

        # Botões com sinais
        self.sync_btn = QPushButton("Sync REC")
        self.export_btn = QPushButton("Exportar")
        self.caption_btn = QPushButton("Legenda")
        self.record_btn = QPushButton("REC")

        for btn in [self.sync_btn, self.export_btn, self.caption_btn, self.record_btn]:
            btn.setFixedHeight(40)
            btn.setStyleSheet(
                "QPushButton {background-color: #555; color: white; border-radius: 6px;}"
                "QPushButton:hover {background-color: #777;}"
            )
            self.layout.addWidget(btn)

        # Conexões dos botões aos sinais
        self.sync_btn.clicked.connect(self.sync_clicked.emit)
        self.export_btn.clicked.connect(self.export_clicked.emit)
        self.caption_btn.clicked.connect(self.caption_clicked.emit)
        self.record_btn.clicked.connect(self.record_clicked.emit)

        self.layout.addStretch()
