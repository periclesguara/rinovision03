import sys
import os
import cv2

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QFileDialog,
    QHBoxLayout,
    QSizePolicy,
    QComboBox,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QLabel,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QImage


class BaseWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("RinoVision - BaseWindow")
        self.setGeometry(100, 100, 1280, 720)

        # Variáveis de controle
        self.file_path = None
        self.cap = None
        self.fps = 30
        self.loop_video = True

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.setup_ui()

    def setup_ui(self):
        # Área de preview com QGraphicsView
        self.view = QGraphicsView()
        self.view.setStyleSheet("border: 2px dashed #555;")
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)

        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)

        # Botões e controles
        self.select_btn = QPushButton("Selecionar Arquivo")
        self.select_btn.clicked.connect(self.open_file)

        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.play_video)
        self.play_btn.setEnabled(False)

        self.pause_btn = QPushButton("Pause")
        self.pause_btn.clicked.connect(self.pause_video)
        self.pause_btn.setEnabled(False)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_video)
        self.stop_btn.setEnabled(False)

        self.input_combo = QComboBox()
        self.input_combo.addItems(["Arquivo", "Webcam"])
        self.input_combo.currentIndexChanged.connect(self.switch_input)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.select_btn)
        button_layout.addWidget(self.input_combo)
        button_layout.addStretch()
        button_layout.addWidget(self.play_btn)
        button_layout.addWidget(self.pause_btn)
        button_layout.addWidget(self.stop_btn)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.view)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def switch_input(self):
        input_type = self.input_combo.currentText()
        self.release_video()

        if input_type == "Webcam":
            self.cap = cv2.VideoCapture(0)

            if not self.cap.isOpened():
                self.scene.clear()
                self.scene.addText("Erro ao abrir a webcam.")
                self.cap.release()
                self.cap = None
                return

            self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
            self.set_buttons_state(True)
            self.select_btn.setEnabled(False)

        elif input_type == "Arquivo":
            self.set_buttons_state(False)
            self.select_btn.setEnabled(True)
            self.scene.clear()
            self.scene.addText("Nenhum arquivo carregado")

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Arquivo",
            "",
            "Imagens e Vídeos (*.jpg *.jpeg *.png *.bmp *.mp4 *.avi *.mkv *.mov)",
        )

        if not file_path:
            return

        self.file_path = file_path
        ext = os.path.splitext(file_path)[1].lower()

        self.release_video()

        if ext in [".jpg", ".jpeg", ".png", ".bmp"]:
            self.load_image(file_path)
        elif ext in [".mp4", ".avi", ".mkv", ".mov"]:
            self.load_video(file_path)

    def load_image(self, path):
        pix = QPixmap(path)
        self.pixmap_item.setPixmap(pix)
        self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.set_buttons_state(False)

    def load_video(self, path):
        self.cap = cv2.VideoCapture(path)

        if not self.cap.isOpened():
            self.scene.clear()
            self.scene.addText("Erro ao abrir o vídeo.")
            self.cap.release()
            self.cap = None
            return

        fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.fps = fps if fps > 1 else 30

        self.set_buttons_state(True)
        self.update_frame()

    def play_video(self):
        if self.cap:
            self.timer.start(int(1000 / self.fps))

    def pause_video(self):
        self.timer.stop()

    def stop_video(self):
        self.timer.stop()
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.update_frame()

    def update_frame(self):
        if self.cap:
            ret, frame = self.cap.read()

            if not ret:
                if self.loop_video:
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    return
                else:
                    self.stop_video()
                    return

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w

            qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pix = QPixmap.fromImage(qt_image)

            self.pixmap_item.setPixmap(pix)
            self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def release_video(self):
        if self.cap:
            self.cap.release()
            self.cap = None
        self.timer.stop()

    def set_buttons_state(self, enabled: bool):
        self.play_btn.setEnabled(enabled)
        self.pause_btn.setEnabled(enabled)
        self.stop_btn.setEnabled(enabled)

    def closeEvent(self, event):
        self.release_video()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BaseWindow()
    window.show()
    sys.exit(app.exec())
