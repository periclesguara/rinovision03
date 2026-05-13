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
from rinovision.studio_composer.video_playback import VideoLayerPlayer
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
        self.video_timer = QTimer(self)
        self.video_timer.timeout.connect(self.update_video_frames)
        self.video_players = {}
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
            ("Play/Pause", self.toggle_selected_video_playback),
            ("Webcam", self.toggle_webcam),
            ("Scale +", self.scale_selected_up),
            ("Scale -", self.scale_selected_down),
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
            layer.metadata["playback"] = "paused"
            preview = create_video_preview_frame(layer.source_path, self.controller.scene.project_id)
            if preview.get("ok") and preview.get("preview_path"):
                self.canvas.add_layer_pixmap(layer, QPixmap(preview["preview_path"]))
            else:
                self.canvas.add_placeholder_layer(layer)
        self._refresh_inspector()

    def toggle_selected_video_playback(self):
        layer_id = self.canvas.selected_layer_id()
        if not layer_id:
            return
        layer = next((item for item in self.controller.scene.layers if item.id == layer_id), None)
        if layer is None or layer.layer_type != "video":
            return
        player = self.video_players.get(layer.id)
        if player and player.is_playing():
            player.pause()
            layer.metadata["playback"] = "paused"
            self._refresh_inspector(layer.id)
            return
        player = VideoLayerPlayer(layer.source_path)
        status = player.play()
        if not status.get("ok"):
            layer.metadata["playback"] = "unavailable"
            layer.metadata["playback_error"] = status.get("error", "")
            self._refresh_inspector(layer.id)
            return
        self.video_players[layer.id] = player
        layer.metadata["playback"] = "playing"
        if not self.video_timer.isActive():
            self.video_timer.start(33)
        self._refresh_inspector(layer.id)

    def update_video_frames(self):
        active = False
        for layer_id, player in list(self.video_players.items()):
            if not player.is_playing():
                continue
            layer = next((item for item in self.controller.scene.layers if item.id == layer_id), None)
            if layer is None:
                player.pause()
                continue
            frame = player.read_frame()
            if frame is None:
                layer.metadata["playback"] = "paused"
                continue
            cv2 = player._cv2
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.canvas.set_video_frame(layer, frame_rgb)
            active = True
        if not active:
            self.video_timer.stop()

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

    def scale_selected_up(self):
        self.scale_selected(1.1)

    def scale_selected_down(self):
        self.scale_selected(0.9)

    def scale_selected(self, factor: float):
        layer_id = self.canvas.selected_layer_id()
        if not layer_id:
            return
        layer = next((item for item in self.controller.scene.layers if item.id == layer_id), None)
        if layer is None:
            return
        self.canvas.scale_layer_item(layer, factor)
        try:
            self.controller.scale_layer(layer.id, layer.scale)
        except ValueError:
            return
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
                "playback": layer.metadata.get("playback", "-"),
            }
        )

    def closeEvent(self, event):
        self.timer.stop()
        self.video_timer.stop()
        self.webcam.stop_preview()
        for player in self.video_players.values():
            player.pause()
        super().closeEvent(event)


def launch_studio_composer() -> int:
    if _IMPORT_ERROR:
        print(f"PySide6 is required for Studio Composer UI: {_IMPORT_ERROR}")
        return 1
    app = QApplication.instance() or QApplication([])
    window = StudioComposerWindow()
    window.show()
    return app.exec()
