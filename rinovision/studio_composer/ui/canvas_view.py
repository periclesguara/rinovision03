try:
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QColor, QImage, QPixmap
    from PySide6.QtWidgets import QGraphicsScene, QGraphicsView
    _IMPORT_ERROR = None
except ImportError as exc:
    Qt = QColor = QImage = QPixmap = QGraphicsScene = QGraphicsView = None
    _IMPORT_ERROR = exc

from rinovision.studio_composer.ui.layer_items import MovablePixmapItem, PlaceholderLayerItem, require_pyside


class StudioCanvasView(QGraphicsView if QGraphicsView else object):
    def __init__(self, parent=None):
        require_pyside()
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setSceneRect(0, 0, 1280, 720)
        self.setBackgroundBrush(QColor(18, 20, 24))
        self.items_by_layer_id = {}
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def add_layer_pixmap(self, layer, pixmap):
        pixmap = self._fit_pixmap_to_layer(pixmap, layer)
        item = MovablePixmapItem(pixmap, layer_id=layer.id, layer_name=layer.name)
        self._configure_item(item, layer)
        self.scene.addItem(item)
        self.items_by_layer_id[layer.id] = item
        return item

    def _fit_pixmap_to_layer(self, pixmap, layer):
        target_width = max(1, int(layer.width))
        target_height = max(1, int(layer.height))
        if pixmap.isNull():
            return pixmap
        return pixmap.scaled(target_width, target_height, Qt.AspectRatioMode.KeepAspectRatio)

    def add_placeholder_layer(self, layer):
        item = PlaceholderLayerItem(width=int(layer.width), height=int(layer.height), layer_id=layer.id, layer_name=layer.name)
        self._configure_item(item, layer)
        self.scene.addItem(item)
        self.items_by_layer_id[layer.id] = item
        return item

    def _configure_item(self, item, layer):
        item.setPos(layer.x, layer.y)
        item.setScale(layer.scale)
        item.setRotation(layer.rotation)
        item.setOpacity(layer.opacity)
        item.setZValue(layer.z_index)
        item.setVisible(layer.visible)
        item.set_locked(layer.locked)

    def set_webcam_frame(self, layer, frame):
        height, width, channels = frame.shape
        bytes_per_line = channels * width
        image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(image).scaled(int(layer.width), int(layer.height), Qt.AspectRatioMode.KeepAspectRatio)
        item = self.items_by_layer_id.get(layer.id)
        if item is None:
            item = self.add_layer_pixmap(layer, pixmap)
        else:
            item.setPixmap(pixmap)

    def set_video_frame(self, layer, frame):
        height, width, channels = frame.shape
        bytes_per_line = channels * width
        image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(image).scaled(int(layer.width), int(layer.height), Qt.AspectRatioMode.KeepAspectRatio)
        item = self.items_by_layer_id.get(layer.id)
        if item is None:
            self.add_layer_pixmap(layer, pixmap)
        else:
            item.setPixmap(pixmap)

    def selected_layer_id(self):
        selected = self.scene.selectedItems()
        if not selected:
            return None
        return getattr(selected[0], "layer_id", None)

    def sync_layer_geometry(self, layer):
        item = self.items_by_layer_id.get(layer.id)
        if item is None:
            return layer
        rect = item.boundingRect()
        layer.x = item.x()
        layer.y = item.y()
        layer.width = rect.width()
        layer.height = rect.height()
        layer.scale = item.scale()
        layer.rotation = item.rotation()
        layer.z_index = int(item.zValue())
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

    def sync_all_layers(self, layers):
        for layer in layers:
            self.sync_layer_geometry(layer)

    def lock_items(self, locked: bool):
        for item in self.items_by_layer_id.values():
            item.set_locked(locked)

    def clear_layers(self):
        self.scene.clear()
        self.items_by_layer_id.clear()

    def layer_geometry(self, layer_id: str) -> dict:
        item = self.items_by_layer_id.get(layer_id)
        if item is None:
            return {}
        rect = item.boundingRect()
        return {
            "x": item.x(),
            "y": item.y(),
            "width": rect.width(),
            "height": rect.height(),
            "scale": item.scale(),
            "display_width": rect.width() * item.scale(),
            "display_height": rect.height() * item.scale(),
            "rotation": item.rotation(),
            "z_index": int(item.zValue()),
        }
