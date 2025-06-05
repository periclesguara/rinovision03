import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QComboBox, QSlider,
    QLabel, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QHBoxLayout
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QImage

import cv2
import numpy as np
import mediapipe as mp


class WebcamWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Webcam - Fundo Personalizado")
        self.setGeometry(100, 100, 960, 720)

        # ✔️ Mantém a transparência interna (só do conteúdo, não da janela inteira)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # MediaPipe para segmentação de fundo
        self.mp_selfie_segmentation = mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1)

        # Webcam
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # Interface
        layout = QVBoxLayout(self)

        self.view = QGraphicsView()
        self.view.setStyleSheet("background: transparent;")
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)
        layout.addWidget(self.view)

        # Botões e controles
        control_layout = QHBoxLayout()

        self.toggle_button = QPushButton("Ligar Webcam")
        self.toggle_button.clicked.connect(self.toggle_webcam)
        control_layout.addWidget(self.toggle_button)

        self.bg_combo = QComboBox()
        self.bg_combo.addItems(["Transparente", "Branco", "Preto", "ChromaKey", "Blur"])
        control_layout.addWidget(QLabel("Fundo:"))
        control_layout.addWidget(self.bg_combo)

        self.resize_slider = QSlider(Qt.Horizontal)
        self.resize_slider.setRange(50, 200)
        self.resize_slider.setValue(100)
        control_layout.addWidget(QLabel("Zoom:"))
        control_layout.addWidget(self.resize_slider)

        layout.addLayout(control_layout)

    def toggle_webcam(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("Erro ao abrir a webcam.")
                self.cap = None
                return
            self.timer.start(30)
            self.toggle_button.setText("Desligar Webcam")
        else:
            self.timer.stop()
            self.cap.release()
            self.cap = None
            self.toggle_button.setText("Ligar Webcam")
            self.pixmap_item.setPixmap(QPixmap())

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Segmentação do fundo
        results = self.mp_selfie_segmentation.process(frame_rgb)
        mask = results.segmentation_mask

        bg_color = self.bg_combo.currentText()

        # Cria background conforme escolha
        if bg_color == "Branco":
            background = np.full(frame_rgb.shape, 255, dtype=np.uint8)
        elif bg_color == "Preto":
            background = np.zeros(frame_rgb.shape, dtype=np.uint8)
        elif bg_color == "ChromaKey":
            background = np.full(frame_rgb.shape, (0, 255, 0), dtype=np.uint8)
        elif bg_color == "Blur":
            background = cv2.GaussianBlur(frame_rgb, (55, 55), 0)
        else:  # Transparente visual (preto como neutro visual)
            background = np.zeros(frame_rgb.shape, dtype=np.uint8)

        # Aplicar máscara
        condition = np.stack((mask,) * 3, axis=-1) > 0.5
        output_frame = np.where(condition, frame_rgb, background)

        # Redimensionamento (zoom)
        scale = self.resize_slider.value() / 100.0
        output_frame = cv2.resize(output_frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

        # Conversão para QPixmap
        h, w, ch = output_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(output_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)

        self.pixmap_item.setPixmap(pixmap)
        self.view.fitInView(self.pixmap_item, Qt.KeepAspectRatio)

    def closeEvent(self, event):
        if self.cap:
            self.cap.release()
        self.timer.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WebcamWindow()
    window.show()
    sys.exit(app.exec())
