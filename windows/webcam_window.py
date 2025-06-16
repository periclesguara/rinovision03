import cv2
import numpy as np
import sys
import mediapipe as mp

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QComboBox,
    QSlider,
    QLabel,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QImage


class WebcamWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RinoVision - Webcam PRO")
        self.setGeometry(100, 100, 1280, 720)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.mp_selfie = mp.solutions.selfie_segmentation.SelfieSegmentation(
            model_selection=1
        )
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        layout = QVBoxLayout(self)

        self.view = QGraphicsView()
        self.view.setStyleSheet("background: transparent")
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        layout.addWidget(self.view)

        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)

        control_layout = QHBoxLayout()

        self.toggle_button = QPushButton("Ligar Webcam")
        self.toggle_button.clicked.connect(self.toggle_webcam)
        control_layout.addWidget(self.toggle_button)

        self.bg_combo = QComboBox()
        self.bg_combo.addItems(["Transparente", "Branco", "Preto", "ChromaKey", "Blur"])
        control_layout.addWidget(QLabel("Fundo:"))
        control_layout.addWidget(self.bg_combo)

        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(50, 200)
        self.zoom_slider.setValue(100)
        control_layout.addWidget(QLabel("Zoom:"))
        control_layout.addWidget(self.zoom_slider)

        layout.addLayout(control_layout)
        self.setLayout(layout)

        self.scene.setSceneRect(0, 0, 1280, 720)

    def toggle_webcam(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("Erro ao abrir webcam.")
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
        if self.cap is None:
            return

        ret, frame = self.cap.read()
        if not ret:
            return

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.mp_selfie.process(frame_rgb)
        mask = results.segmentation_mask

        condition = np.stack((mask,) * 3, axis=-1) > 0.5
        bg_choice = self.bg_combo.currentText()

        h, w, _ = frame_rgb.shape
        if bg_choice == "Branco":
            background = np.full(frame_rgb.shape, 255, dtype=np.uint8)
        elif bg_choice == "Preto":
            background = np.zeros(frame_rgb.shape, dtype=np.uint8)
        elif bg_choice == "ChromaKey":
            background = np.full(frame_rgb.shape, (0, 255, 0), dtype=np.uint8)
        elif bg_choice == "Blur":
            background = cv2.GaussianBlur(frame_rgb, (15, 15), 0)
        else:  # Transparente ou default
            background = np.zeros(frame_rgb.shape, dtype=np.uint8)

        output = np.where(condition, frame_rgb, background)

        if bg_choice == "Transparente":
            alpha = (condition[..., 0] * 255).astype(np.uint8)
            output = np.dstack((output, alpha))
            qt_format = QImage.Format_RGBA8888
        else:
            qt_format = QImage.Format_RGB888

        scale = self.zoom_slider.value() / 100.0
        output = cv2.resize(
            output, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA
        )

        h, w, ch = output.shape
        bytes_per_line = ch * w
        qt_image = QImage(output.data, w, h, bytes_per_line, qt_format)

        pixmap = QPixmap.fromImage(qt_image)
        self.pixmap_item.setPixmap(pixmap)

        self.scene.setSceneRect(0, 0, w, h)
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def closeEvent(self, event):
        if self.cap:
            self.cap.release()
        self.timer.stop()
        event.accept()
