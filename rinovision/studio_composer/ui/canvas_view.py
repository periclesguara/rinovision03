try:
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QColor, QImage, QPalette, QPixmap
    from PySide6.QtWidgets import QGraphicsScene, QGraphicsView
    _IMPORT_ERROR = None
except ImportError as exc:
    Qt = QColor = QImage = QPalette = QPixmap = QGraphicsScene = QGraphicsView = None
    _IMPORT_ERROR = exc

from rinovision.studio_composer.ui.layer_items import MovablePixmapItem, PlaceholderLayerItem, require_pyside


class StudioCanvasView(QGraphicsView if QGraphicsView else object):
    def __init__(self, parent=None):
        require_pyside()
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setSceneRect(0, 0, 1280, 720)
        background = QColor(18, 20, 24)
        self.scene.setBackgroundBrush(background)
        self.setBackgroundBrush(background)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setCacheMode(QGraphicsView.CacheModeFlag.CacheNone)
        self.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontSavePainterState, False)
        self.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing, False)
        self.viewport().setAutoFillBackground(True)
        palette = self.viewport().palette()
        palette.setColor(QPalette.ColorRole.Window, background)
        self.viewport().setPalette(palette)
        self.items_by_layer_id = {}
        self.movement_callback = None
        self.resize_callback = None
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def add_layer_pixmap(self, layer, pixmap):
        pixmap = self._fit_pixmap_to_layer(pixmap, layer)
        item = MovablePixmapItem(
            pixmap,
            layer_id=layer.id,
            layer_name=layer.name,
            movement_callback=self.movement_callback,
            resize_callback=self.resize_callback,
        )
        self._configure_item(item, layer)
        self.scene.addItem(item)
        self.items_by_layer_id[layer.id] = item
        self.update_item_z_value(layer.id, layer.computed_z_index)
        return item

    def _fit_pixmap_to_layer(self, pixmap, layer):
        target_width = max(1, int(layer.width))
        target_height = max(1, int(layer.height))
        if pixmap.isNull():
            return pixmap
        return pixmap.scaled(target_width, target_height, Qt.AspectRatioMode.KeepAspectRatio)

    def add_placeholder_layer(self, layer):
        item = PlaceholderLayerItem(
            width=int(layer.width),
            height=int(layer.height),
            layer_id=layer.id,
            layer_name=layer.name,
            movement_callback=self.movement_callback,
            resize_callback=self.resize_callback,
        )
        self._configure_item(item, layer)
        self.scene.addItem(item)
        self.items_by_layer_id[layer.id] = item
        self.update_item_z_value(layer.id, layer.computed_z_index)
        return item

    def get_item_by_layer_id(self, layer_id: str):
        return self.items_by_layer_id.get(layer_id)

    def update_item_z_value(self, layer_id: str, z_value: int) -> bool:
        item = self.get_item_by_layer_id(layer_id)
        if item is None:
            return False
        item.setZValue(z_value)
        item.update()
        self.request_repaint()
        return True

    def sync_item_z_order(self, layer) -> bool:
        item = self.get_item_by_layer_id(layer.id)
        if item is None:
            return False
        item.layer_slot = layer.layer_slot
        return self.update_item_z_value(layer.id, layer.computed_z_index)

    def refresh_all_z_values_from_model(self, layers) -> None:
        for layer in layers:
            self.sync_item_z_order(layer)

    def refresh_layer_order(self, layers) -> None:
        self.refresh_all_z_values_from_model(layers)

    def sync_item_from_layer(self, layer) -> bool:
        item = self.get_item_by_layer_id(layer.id)
        if item is None:
            return False
        item.setPos(layer.x, layer.y)
        item.setScale(layer.scale)
        item.setRotation(layer.rotation)
        item.setOpacity(layer.opacity)
        item.setVisible(layer.visible)
        item.set_locked(layer.locked)
        item.layer_slot = layer.layer_slot
        item.setZValue(layer.computed_z_index)
        item.update()
        self.request_repaint()
        return True

    def select_layer_item(self, layer_id: str) -> bool:
        item = self.get_item_by_layer_id(layer_id)
        if item is None:
            return False
        self.scene.clearSelection()
        item.setSelected(True)
        self.centerOn(item)
        self.request_repaint()
        return True

    def _configure_item(self, item, layer):
        item.layer_type = layer.layer_type
        item.layer_slot = layer.layer_slot
        item.setPos(layer.x, layer.y)
        item.setScale(layer.scale)
        item.setRotation(layer.rotation)
        item.setOpacity(layer.opacity)
        item.setZValue(layer.computed_z_index)
        item.setVisible(layer.visible)
        item.set_locked(layer.locked)
        item.update()
        self.request_repaint()

    def set_webcam_frame(self, layer, frame):
        height, width, channels = frame.shape
        bytes_per_line = channels * width
        image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        target_width, target_height = self._stable_frame_size(layer)
        pixmap = QPixmap.fromImage(image).scaled(target_width, target_height, Qt.AspectRatioMode.KeepAspectRatio)
        item = self.items_by_layer_id.get(layer.id)
        if item is None:
            item = self.add_layer_pixmap(layer, pixmap)
        else:
            item.setPixmap(pixmap)
            item.update()
            self.request_repaint()

    def set_video_frame(self, layer, frame):
        height, width, channels = frame.shape
        bytes_per_line = channels * width
        image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        target_width, target_height = self._stable_frame_size(layer)
        pixmap = QPixmap.fromImage(image).scaled(target_width, target_height, Qt.AspectRatioMode.KeepAspectRatio)
        item = self.items_by_layer_id.get(layer.id)
        if item is None:
            self.add_layer_pixmap(layer, pixmap)
        else:
            item.setPixmap(pixmap)
            item.update()
            self.request_repaint()

    def _stable_frame_size(self, layer) -> tuple[int, int]:
        metadata = getattr(layer, "metadata", {})
        width = metadata.get("frame_width", layer.width)
        height = metadata.get("frame_height", layer.height)
        return max(1, int(width)), max(1, int(height))

    def selected_layer_id(self):
        selected = self.scene.selectedItems()
        if not selected:
            return None
        return getattr(selected[0], "layer_id", None)

    def sync_layer_geometry(self, layer):
        item = self.items_by_layer_id.get(layer.id)
        if item is None:
            return layer
        width, height = item.content_size() if hasattr(item, "content_size") else (item.boundingRect().width(), item.boundingRect().height())
        layer.x = item.x()
        layer.y = item.y()
        if not layer.metadata.get("stable_frame_size"):
            layer.width = width
            layer.height = height
        layer.scale = item.scale()
        layer.rotation = item.rotation()
        layer.computed_z_index = int(item.zValue())
        layer.visible = item.isVisible()
        return layer

    def scale_layer_item(self, layer, factor: float):
        item = self.items_by_layer_id.get(layer.id)
        if item is None or getattr(item, "locked", False):
            return layer
        new_scale = max(0.05, min(10.0, item.scale() * factor))
        item.setScale(new_scale)
        layer.scale = new_scale
        return self.sync_layer_geometry(layer)

    def resize_layer_item(self, layer, width: float, height: float):
        item = self.items_by_layer_id.get(layer.id)
        if item is None or getattr(item, "locked", False):
            return layer
        if hasattr(item, "resize_to") and item.resize_to(width, height):
            layer.width = width
            layer.height = height
        return self.sync_layer_geometry(layer)

    def sync_all_layers(self, layers):
        for layer in layers:
            self.sync_layer_geometry(layer)

    def lock_items(self, locked: bool):
        for item in self.items_by_layer_id.values():
            item.set_locked(locked)
        self.request_repaint()

    def clear_layers(self):
        self.scene.clear()
        self.items_by_layer_id.clear()
        self.request_repaint()

    def request_repaint(self):
        self.scene.update(self.sceneRect())
        self.viewport().update()

    def layer_geometry(self, layer_id: str) -> dict:
        item = self.items_by_layer_id.get(layer_id)
        if item is None:
            return {}
        width, height = item.content_size() if hasattr(item, "content_size") else (item.boundingRect().width(), item.boundingRect().height())
        return {
            "x": item.x(),
            "y": item.y(),
            "width": width,
            "height": height,
            "scale": item.scale(),
            "display_width": width * item.scale(),
            "display_height": height * item.scale(),
            "rotation": item.rotation(),
            "computed_z_index": int(item.zValue()),
        }
