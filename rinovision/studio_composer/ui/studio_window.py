try:
    from PySide6.QtCore import QTimer
    from PySide6.QtGui import QPixmap
    from PySide6.QtWidgets import QApplication, QFileDialog, QComboBox, QLabel, QHBoxLayout, QPushButton, QVBoxLayout, QWidget
    _IMPORT_ERROR = None
except ImportError as exc:
    QApplication = QFileDialog = QComboBox = QLabel = QHBoxLayout = QPushButton = QTimer = QVBoxLayout = QWidget = QPixmap = None
    _IMPORT_ERROR = exc

import os

from rinovision.studio_composer.controller import StudioComposerController
from rinovision.studio_composer.ui.canvas_view import StudioCanvasView
from rinovision.studio_composer.ui.inspector_panel import InspectorPanel
from rinovision.studio_composer.ui.layer_items import require_pyside
from rinovision.studio_composer.video_playback import VideoLayerPlayer
from rinovision.studio_composer.video_preview import create_video_preview_frame
from rinovision.studio_composer.webcam_enhancement import apply_webcam_enhancement, default_webcam_enhancement
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
        self.canvas.movement_callback = self.on_layer_moved
        self.canvas.resize_callback = self.on_layer_resized
        self.inspector = InspectorPanel(self)
        self.layer_panel = QLabel("")
        self._syncing_slot_combo = False
        self.debug_layer_assignment = os.getenv("RINOVISION_STUDIO_DEBUG") == "1"
        self._build_ui()
        self.canvas.scene.selectionChanged.connect(self.on_selection_changed)
        self._refresh_layer_panel()
        self._refresh_inspector()

    def _build_ui(self):
        root = QHBoxLayout(self)
        left = QVBoxLayout()
        toolbar = QHBoxLayout()
        self.image_layer_slot_combo = self._make_slot_select(default_slot=2)
        self.video_layer_slot_combo = self._make_slot_select(default_slot=2)
        self.webcam_layer_slot_combo = self._make_slot_select(default_slot=1)
        self.selected_layer_slot_combo = self._make_slot_select(default_slot=1)
        self.selected_layer_slot_combo.currentIndexChanged.connect(self.on_selected_slot_changed)
        toolbar.addWidget(QLabel("Image Layer"))
        toolbar.addWidget(self.image_layer_slot_combo)
        toolbar.addWidget(QLabel("Video Layer"))
        toolbar.addWidget(self.video_layer_slot_combo)
        toolbar.addWidget(QLabel("Webcam Layer"))
        toolbar.addWidget(self.webcam_layer_slot_combo)
        toolbar.addWidget(QLabel("Selected Layer"))
        toolbar.addWidget(self.selected_layer_slot_combo)
        buttons = [
            ("Upload Image", self.upload_images),
            ("Upload Video", self.upload_videos),
            ("Play/Pause", self.toggle_selected_video_playback),
            ("Webcam", self.toggle_webcam),
            ("Bright +", self.webcam_brightness_up),
            ("Bright -", self.webcam_brightness_down),
            ("Contrast +", self.webcam_contrast_up),
            ("Contrast -", self.webcam_contrast_down),
            ("Sat +", self.webcam_saturation_up),
            ("Sat -", self.webcam_saturation_down),
            ("Mirror", self.toggle_webcam_mirror),
            ("Reset Cam", self.reset_webcam_image),
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
        self.layer_panel.setWordWrap(True)
        left.addWidget(self.layer_panel)
        root.addLayout(left, 4)
        root.addWidget(self.inspector, 1)

    def _make_slot_select(self, default_slot: int):
        combo = QComboBox()
        for slot in self.controller.scene.layer_slots:
            combo.addItem(f"{slot.name}", slot.slot_number)
        index = combo.findData(default_slot)
        if index >= 0:
            combo.setCurrentIndex(index)
        return combo

    def _selected_image_slot(self) -> int:
        return int(self.image_layer_slot_combo.currentData())

    def _selected_video_slot(self) -> int:
        return int(self.video_layer_slot_combo.currentData())

    def _selected_webcam_slot(self) -> int:
        return int(self.webcam_layer_slot_combo.currentData())

    def _selected_target_slot(self) -> int:
        return int(self.selected_layer_slot_combo.currentData())

    def upload_images(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Select image", "", "Images (*.png *.jpg *.jpeg *.webp)")
        for path in paths:
            self.add_image_path_to_selected_slot(path)
        self._refresh_layer_panel()
        self._refresh_inspector()

    def upload_videos(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "Select video", "", "Videos (*.mp4 *.mov *.mkv *.webm)")
        for path in paths:
            self.add_video_path_to_selected_slot(path)
        self._refresh_layer_panel()
        self._refresh_inspector()

    def add_image_path_to_selected_slot(self, path):
        selected_slot = self._selected_image_slot()
        layer = self.controller.add_image_layer(path, layer_slot=selected_slot)
        self.canvas.add_layer_pixmap(layer, QPixmap(layer.source_path))
        self.canvas.sync_item_z_order(layer)
        self.canvas.select_layer_item(layer.id)
        self._debug_source_assignment("image", selected_slot, layer)
        self._refresh_layer_panel()
        self._refresh_inspector(layer.id)
        return layer

    def add_video_path_to_selected_slot(self, path):
        selected_slot = self._selected_video_slot()
        layer = self.controller.add_video_layer(path, layer_slot=selected_slot)
        layer.metadata["playback"] = "paused"
        preview = create_video_preview_frame(layer.source_path, self.controller.scene.project_id)
        if preview.get("ok") and preview.get("preview_path"):
            self.canvas.add_layer_pixmap(layer, QPixmap(preview["preview_path"]))
        else:
            self.canvas.add_placeholder_layer(layer)
        self.canvas.sync_item_z_order(layer)
        self.canvas.select_layer_item(layer.id)
        self._debug_source_assignment("video", selected_slot, layer)
        self._refresh_layer_panel()
        self._refresh_inspector(layer.id)
        return layer

    def add_webcam_layer_to_selected_slot(self, enabled: bool = False, camera_id: int = 0):
        selected_slot = self._selected_webcam_slot()
        layer = self.controller.add_webcam_layer(
            enabled=enabled,
            camera_id=camera_id,
            mode="free_floating",
            layer_slot=selected_slot,
        )
        item = self.canvas.get_item_by_layer_id(layer.id)
        if item is not None:
            item.setVisible(layer.visible)
            self.canvas.sync_item_z_order(layer)
            self.canvas.select_layer_item(layer.id)
        self._debug_source_assignment("webcam", selected_slot, layer)
        self._refresh_layer_panel()
        self._refresh_inspector(layer.id)
        return layer

    def _debug_source_assignment(self, source_type: str, selected_slot: int, layer):
        if not self.debug_layer_assignment:
            return
        item = self.canvas.get_item_by_layer_id(layer.id)
        z_value = item.zValue() if item is not None else None
        print(
            f"Added {source_type}: "
            f"selected_slot={selected_slot} "
            f"model.layer_slot={layer.layer_slot} "
            f"computed_z_index={layer.computed_z_index} "
            f"item.zValue={z_value}"
        )

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
            layer = self.add_webcam_layer_to_selected_slot(enabled=False)
            return
        status = self.webcam.start_preview()
        if status.get("ok"):
            layer = self.add_webcam_layer_to_selected_slot(enabled=True, camera_id=0)
            self.timer.start(33)

    def update_webcam_frame(self):
        frame = self.webcam.read_frame()
        if frame is None:
            return
        layer = self.controller.scene.webcam_layer
        cv2 = self.webcam.preview._cv2
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = apply_webcam_enhancement(frame_rgb, layer.metadata.get("enhancement"))
        self.canvas.set_webcam_frame(layer, frame_rgb)

    def on_selection_changed(self):
        for item in self.canvas.items_by_layer_id.values():
            item.update()
        layer_id = self.canvas.selected_layer_id()
        if layer_id:
            try:
                self.controller.select_layer(layer_id)
            except (AttributeError, KeyError):
                layer_id = None
        self._refresh_inspector(layer_id)
        self.canvas.request_repaint()

    def on_layer_moved(self, layer_id: str, x: float, y: float):
        try:
            self.controller.move_layer(layer_id, x, y)
        except ValueError:
            item = self.canvas.get_item_by_layer_id(layer_id)
            layer = next((candidate for candidate in self.controller.scene.layers if getattr(candidate, "id", None) == layer_id), None)
            if item is not None and layer is not None:
                item.setPos(layer.x, layer.y)
                item.update()
                self.canvas.request_repaint()
            return
        if self.controller.scene.selected_layer_id == layer_id:
            self._refresh_inspector(layer_id)
        item = self.canvas.get_item_by_layer_id(layer_id)
        if item is not None:
            item.update()
        self.canvas.request_repaint()

    def on_layer_resized(self, layer_id: str, width: float, height: float):
        try:
            layer = self.controller.resize_layer(layer_id, width, height)
        except ValueError:
            item = self.canvas.get_item_by_layer_id(layer_id)
            layer = next((candidate for candidate in self.controller.scene.layers if getattr(candidate, "id", None) == layer_id), None)
            if item is not None and layer is not None and hasattr(item, "_apply_size"):
                item._apply_size(int(layer.width), int(layer.height))
            return
        if layer.metadata.get("stable_frame_size"):
            layer.metadata["frame_width"] = width
            layer.metadata["frame_height"] = height
        self.canvas.sync_item_z_order(layer)
        if self.controller.scene.selected_layer_id == layer_id:
            self._refresh_inspector(layer_id)
        self.canvas.request_repaint()

    def bring_selected_forward(self):
        layer_id = self.canvas.selected_layer_id()
        if not layer_id:
            return
        layer = self.controller.bring_forward(layer_id)
        self.canvas.sync_item_z_order(layer)
        self._refresh_inspector(layer.id)
        self.canvas.request_repaint()

    def send_selected_backward(self):
        layer_id = self.canvas.selected_layer_id()
        if not layer_id:
            return
        layer = self.controller.send_backward(layer_id)
        self.canvas.sync_item_z_order(layer)
        self._refresh_inspector(layer.id)
        self.canvas.request_repaint()

    def move_selected_to_slot(self):
        layer_id = self.canvas.selected_layer_id()
        if not layer_id:
            return
        try:
            layer = self.controller.move_layer_to_slot(layer_id, self._selected_target_slot())
        except ValueError:
            layer = next((item for item in self.controller.scene.layers if item.id == layer_id), None)
            if layer is not None:
                self._set_selected_slot_combo(layer.layer_slot)
            return
        self.canvas.sync_item_z_order(layer)
        self._refresh_layer_panel()
        self._refresh_inspector(layer.id)
        self.canvas.request_repaint()

    def on_selected_slot_changed(self, *_args):
        if self._syncing_slot_combo:
            return
        self.move_selected_to_slot()

    def scale_selected_up(self):
        self.scale_selected(1.1)

    def scale_selected_down(self):
        self.scale_selected(0.9)

    def _selected_webcam_layer(self):
        layer_id = self.canvas.selected_layer_id() or self.controller.scene.webcam_layer.id
        layer = next((item for item in self.controller.scene.layers if item.id == layer_id), None)
        if layer is None or layer.layer_type != "webcam":
            return None
        layer.metadata.setdefault("enhancement", default_webcam_enhancement())
        return layer

    def _adjust_webcam_enhancement(self, key: str, delta: float, min_value=None, max_value=None):
        layer = self._selected_webcam_layer()
        if layer is None:
            return
        enhancement = layer.metadata.setdefault("enhancement", default_webcam_enhancement())
        value = float(enhancement.get(key, default_webcam_enhancement()[key])) + delta
        if min_value is not None:
            value = max(min_value, value)
        if max_value is not None:
            value = min(max_value, value)
        enhancement[key] = round(value, 3)
        self._refresh_inspector(layer.id)
        self.canvas.request_repaint()

    def webcam_brightness_up(self):
        self._adjust_webcam_enhancement("brightness", 10, -100, 100)

    def webcam_brightness_down(self):
        self._adjust_webcam_enhancement("brightness", -10, -100, 100)

    def webcam_contrast_up(self):
        self._adjust_webcam_enhancement("contrast", 0.1, 0.1, 3.0)

    def webcam_contrast_down(self):
        self._adjust_webcam_enhancement("contrast", -0.1, 0.1, 3.0)

    def webcam_saturation_up(self):
        self._adjust_webcam_enhancement("saturation", 0.1, 0.0, 3.0)

    def webcam_saturation_down(self):
        self._adjust_webcam_enhancement("saturation", -0.1, 0.0, 3.0)

    def toggle_webcam_mirror(self):
        layer = self._selected_webcam_layer()
        if layer is None:
            return
        enhancement = layer.metadata.setdefault("enhancement", default_webcam_enhancement())
        enhancement["mirror"] = not bool(enhancement.get("mirror", True))
        self._refresh_inspector(layer.id)

    def reset_webcam_image(self):
        layer = self._selected_webcam_layer()
        if layer is None:
            return
        layer.metadata["enhancement"] = default_webcam_enhancement()
        self._refresh_inspector(layer.id)

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
        self._set_slot_controls_enabled(False)
        self._refresh_inspector(self.controller.scene.selected_layer_id)
        self.canvas.request_repaint()

    def unlock_layout(self):
        self.controller.unlock_scene()
        self.canvas.lock_items(False)
        self._set_slot_controls_enabled(True)
        self._refresh_inspector(self.controller.scene.selected_layer_id)
        self.canvas.request_repaint()

    def reset_selected_layer(self):
        layer_id = self.canvas.selected_layer_id()
        if not layer_id:
            return
        layer = self.controller.move_layer(layer_id, 0, 0)
        layer.scale = 1.0
        item = self.canvas.get_item_by_layer_id(layer_id)
        if item:
            item.setPos(0, 0)
            item.setScale(1.0)
            item.update()
        self._refresh_inspector(layer_id)
        self.canvas.request_repaint()

    def _refresh_inspector(self, layer_id: str | None = None):
        if layer_id is None:
            layer_id = self.controller.scene.selected_layer_id
        layer = None
        if layer_id:
            layer = next((item for item in self.controller.scene.layers if getattr(item, "id", None) == layer_id), None)
        if layer is None:
            self.inspector.update_values({})
            return
        self.canvas.sync_layer_geometry(layer)
        self._set_selected_slot_combo(layer.layer_slot)
        self.inspector.update_values(
            {
                "layer_id": layer.id,
                "layer_name": layer.name,
                "layer_type": layer.layer_type,
                "layer_slot": layer.layer_slot,
                "x": round(layer.x, 2),
                "y": round(layer.y, 2),
                "width": round(layer.width, 2),
                "height": round(layer.height, 2),
                "scale": round(layer.scale, 3),
                "local_z_index": layer.local_z_index,
                "computed_z_index": layer.computed_z_index,
                "visible": layer.visible,
                "locked": layer.locked or self.controller.scene.locked,
                "playback": layer.metadata.get("playback", "-"),
                **layer.metadata.get("enhancement", {}),
            }
        )

    def _refresh_layer_panel(self):
        grouped = self.controller.get_scene_layers_grouped_by_slot()
        lines = []
        for slot in self.controller.scene.layer_slots:
            layers = grouped.get(slot.slot_number, [])
            names = ", ".join(layer.name for layer in layers) if layers else "empty"
            lines.append(f"{slot.name} - {slot.description}: {names}")
        self.layer_panel.setText("\n".join(lines))

    def _set_selected_slot_combo(self, layer_slot: int):
        index = self.selected_layer_slot_combo.findData(layer_slot)
        if index < 0:
            return
        self._syncing_slot_combo = True
        self.selected_layer_slot_combo.setCurrentIndex(index)
        self._syncing_slot_combo = False

    def _set_slot_controls_enabled(self, enabled: bool):
        self.image_layer_slot_combo.setEnabled(enabled)
        self.video_layer_slot_combo.setEnabled(enabled)
        self.webcam_layer_slot_combo.setEnabled(enabled)
        self.selected_layer_slot_combo.setEnabled(enabled)

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
