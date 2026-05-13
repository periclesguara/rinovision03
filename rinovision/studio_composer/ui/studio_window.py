try:
    from PySide6.QtCore import QTimer
    from PySide6.QtGui import QPixmap
    from PySide6.QtWidgets import QApplication, QFileDialog, QHBoxLayout, QPushButton, QVBoxLayout, QWidget
    _IMPORT_ERROR = None
except ImportError as exc:
    QApplication = QFileDialog = QHBoxLayout = QPushButton = QTimer = QVBoxLayout = QWidget = QPixmap = None
    _IMPORT_ERROR = exc

from rinovision.studio_composer.controller import StudioComposerController
from rinovision.studio_composer.ui.canvas_view import StudioCanvasView
from rinovision.studio_composer.ui.inspector_panel import InspectorPanel
from rinovision.studio_composer.ui.layer_items import require_pyside
from rinovision.studio_composer.video_preview import create_video_preview_frame
from rinovision.studio_composer.webcam_overlay import WebcamOverlayController


class StudioComposerWindow(QWidget if QWidget else object):
    def __init__(self):
        require_pyside()
        super().__init__()
        self.setWindowTitle("RinoVision Studio Composer")
        self.resize(1500, 860)
        self.controller = StudioComposerController()
        self.webcam = WebcamOverlayController(camera_id=0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_webcam_frame)
        self.canvas = StudioCanvasView(self)
        self.inspector = InspectorPanel(self)
        self._build_ui()
        self.canvas.scene.selectionChanged.connect(self.on_selection_changed)
        self._refresh_inspector()

    def _build_ui(self):
        root = QHBoxLayout(self)
        left = QVBoxLayout()
        toolbar = QHBoxLayout()
        buttons = [
            ("Upload Image", self.upload_images),
            ("Upload Video", self.upload_videos),
            ("Webcam", self.toggle_webcam),
            ("Forward", self.bring_selected_forward),
            ("Backward", self.send_selected_backward),
            ("Lock", self.lock_layout),
            ("Unlock", self.unlock_layout),
            ("Reset Layer", self.reset_selected_layer),
        ]
        for text, callback in buttons:
            button = QPushButton(text)
            button.clicked.connect(callback)
            toolbar.addWidget(button)
        left.addLayout(toolbar)
        left.addWidget(self.canvas)
        root.addLayout(left, 4)
        root.addWidget(self.inspector, 1)

    def upload_images(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Select image", "", "Images (*.png *.jpg *.jpeg *.webp)")
        for path in paths:
            layer = self.controller.add_image_layer(path)
            self.canvas.add_layer_pixmap(layer, QPixmap(layer.source_path))
        self._refresh_inspector()

    def upload_videos(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Select video", "", "Videos (*.mp4 *.mov *.mkv *.webm)")
        for path in paths:
            layer = self.controller.add_video_layer(path)
            preview = create_video_preview_frame(layer.source_path, self.controller.scene.project_id)
            if preview.get("ok") and preview.get("preview_path"):
                self.canvas.add_layer_pixmap(layer, QPixmap(preview["preview_path"]))
            else:
                self.canvas.add_placeholder_layer(layer)
        self._refresh_inspector()

    def toggle_webcam(self):
        if self.webcam.preview.is_running():
            self.timer.stop()
            self.webcam.stop_preview()
            layer = self.controller.add_webcam_layer(enabled=False)
            if layer.id in self.canvas.items_by_layer_id:
                self.canvas.items_by_layer_id[layer.id].setVisible(False)
            self._refresh_inspector(layer.id)
            return
        status = self.webcam.start_preview()
        if status.get("ok"):
            layer = self.controller.add_webcam_layer(enabled=True, camera_id=0, mode="free_floating")
            self.timer.start(33)
            self._refresh_inspector(layer.id)

    def update_webcam_frame(self):
        frame = self.webcam.read_frame()
        if frame is None:
            return
        layer = self.controller.scene.webcam_layer
        cv2 = self.webcam.preview._cv2
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.canvas.set_webcam_frame(layer, frame_rgb)
        self._refresh_inspector(layer.id)

    def on_selection_changed(self):
        layer_id = self.canvas.selected_layer_id()
        if layer_id:
            self.controller.select_layer(layer_id)
        self._refresh_inspector(layer_id)

    def bring_selected_forward(self):
        layer_id = self.canvas.selected_layer_id()
        if not layer_id:
            return
        layer = self.controller.bring_forward(layer_id)
        self.canvas.items_by_layer_id[layer.id].setZValue(layer.z_index)
        self._refresh_inspector(layer.id)

    def send_selected_backward(self):
        layer_id = self.canvas.selected_layer_id()
        if not layer_id:
            return
        layer = self.controller.send_backward(layer_id)
        self.canvas.items_by_layer_id[layer.id].setZValue(layer.z_index)
        self._refresh_inspector(layer.id)

    def lock_layout(self):
        self.canvas.sync_all_layers(self.controller.scene.layers)
        self.controller.lock_scene()
        self.canvas.lock_items(True)
        self._refresh_inspector(self.controller.scene.selected_layer_id)

    def unlock_layout(self):
        self.controller.unlock_scene()
        self.canvas.lock_items(False)
        self._refresh_inspector(self.controller.scene.selected_layer_id)

    def reset_selected_layer(self):
        layer_id = self.canvas.selected_layer_id()
        if not layer_id:
            return
        layer = self.controller.move_layer(layer_id, 0, 0)
        layer.scale = 1.0
        item = self.canvas.items_by_layer_id.get(layer_id)
        if item:
            item.setPos(0, 0)
            item.setScale(1.0)
        self._refresh_inspector(layer_id)

    def _refresh_inspector(self, layer_id: str | None = None):
        if layer_id is None:
            layer_id = self.controller.scene.selected_layer_id
        layer = None
        if layer_id:
            layer = next((item for item in self.controller.scene.layers if item.id == layer_id), None)
        if layer is None:
            self.inspector.update_values({})
            return
        self.canvas.sync_layer_geometry(layer)
        self.inspector.update_values(
            {
                "layer_id": layer.id,
                "layer_name": layer.name,
                "layer_type": layer.layer_type,
                "x": round(layer.x, 2),
                "y": round(layer.y, 2),
                "width": round(layer.width, 2),
                "height": round(layer.height, 2),
                "scale": round(layer.scale, 3),
                "z_index": layer.z_index,
                "visible": layer.visible,
                "locked": layer.locked or self.controller.scene.locked,
            }
        )

    def closeEvent(self, event):
        self.timer.stop()
        self.webcam.stop_preview()
        super().closeEvent(event)


def launch_studio_composer() -> int:
    if _IMPORT_ERROR:
        print(f"PySide6 is required for Studio Composer UI: {_IMPORT_ERROR}")
        return 1
    app = QApplication.instance() or QApplication([])
    window = StudioComposerWindow()
    window.show()
    return app.exec()
