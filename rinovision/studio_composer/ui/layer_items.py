try:
    from PySide6.QtCore import Qt, QRectF
    from PySide6.QtGui import QBrush, QColor, QPen
    from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsRectItem
    _IMPORT_ERROR = None
except ImportError as exc:
    Qt = QRectF = QBrush = QColor = QPen = QGraphicsPixmapItem = QGraphicsRectItem = None
    _IMPORT_ERROR = exc


def require_pyside():
    if _IMPORT_ERROR:
        raise RuntimeError(f"PySide6 is required for Studio Composer UI: {_IMPORT_ERROR}") from _IMPORT_ERROR


class _LayerMixin:
    HANDLE_SIZE = 10
    MIN_SIZE = 24

    def configure_layer(self, layer_id: str, layer_name: str, movement_callback=None, resize_callback=None):
        self.layer_id = layer_id
        self.layer_name = layer_name
        self.locked = False
        self.movement_callback = movement_callback
        self.resize_callback = resize_callback
        self._resize_corner = None
        self._resize_start_scene_pos = None
        self._resize_start_item_pos = None
        self._resize_start_width = 0
        self._resize_start_height = 0
        self._resize_source_pixmap = None
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(self.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)

    def set_locked(self, locked: bool):
        self.locked = locked
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable, not locked)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, not locked)
        self.update()

    def itemChange(self, change, value):
        if (
            change == self.GraphicsItemChange.ItemPositionHasChanged
            and self.movement_callback
            and not self.locked
            and not self._resize_corner
        ):
            self.movement_callback(self.layer_id, value.x(), value.y())
        return super().itemChange(change, value)

    def _corner_rects(self):
        rect = self.boundingRect()
        size = self.HANDLE_SIZE
        half = size / 2
        return {
            "top_left": QRectF(rect.left() - half, rect.top() - half, size, size),
            "top_right": QRectF(rect.right() - half, rect.top() - half, size, size),
            "bottom_left": QRectF(rect.left() - half, rect.bottom() - half, size, size),
            "bottom_right": QRectF(rect.right() - half, rect.bottom() - half, size, size),
        }

    def _corner_at(self, pos):
        if self.locked:
            return None
        for name, rect in self._corner_rects().items():
            if rect.contains(pos):
                return name
        return None

    def paint_resize_handles(self, painter):
        if not self.isSelected() or self.locked:
            return
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.setPen(QPen(QColor(35, 100, 220), 1))
        for rect in self._corner_rects().values():
            painter.drawRect(rect)

    def hoverMoveEvent(self, event):
        corner = self._corner_at(event.pos())
        if corner:
            if corner in {"top_left", "bottom_right"}:
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            else:
                self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        else:
            self.unsetCursor()
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event):
        corner = self._corner_at(event.pos())
        if corner and event.button() == Qt.MouseButton.LeftButton:
            self._resize_corner = corner
            self._resize_start_scene_pos = event.scenePos()
            self._resize_start_item_pos = self.pos()
            self._resize_start_width, self._resize_start_height = self.content_size()
            self._resize_source_pixmap = self._current_pixmap()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._resize_corner:
            self._resize_from_scene_pos(event.scenePos())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._resize_corner:
            self._resize_from_scene_pos(event.scenePos())
            self._resize_corner = None
            self._resize_start_scene_pos = None
            self._resize_start_item_pos = None
            self._resize_source_pixmap = None
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def resize_to(self, width: float, height: float) -> bool:
        if self.locked:
            return False
        width = max(self.MIN_SIZE, int(width))
        height = max(self.MIN_SIZE, int(height))
        self._apply_size(width, height)
        if self.resize_callback:
            self.resize_callback(self.layer_id, width, height)
        self.update()
        return True

    def _resize_from_scene_pos(self, scene_pos):
        delta = scene_pos - self._resize_start_scene_pos
        width = self._resize_start_width
        height = self._resize_start_height
        new_x = self._resize_start_item_pos.x()
        new_y = self._resize_start_item_pos.y()
        if "right" in self._resize_corner:
            width += delta.x()
        if "left" in self._resize_corner:
            width -= delta.x()
            new_x += delta.x()
        if "bottom" in self._resize_corner:
            height += delta.y()
        if "top" in self._resize_corner:
            height -= delta.y()
            new_y += delta.y()
        if width < self.MIN_SIZE:
            if "left" in self._resize_corner:
                new_x -= self.MIN_SIZE - width
            width = self.MIN_SIZE
        if height < self.MIN_SIZE:
            if "top" in self._resize_corner:
                new_y -= self.MIN_SIZE - height
            height = self.MIN_SIZE
        self.setPos(new_x, new_y)
        self.resize_to(width, height)

    def _current_pixmap(self):
        return None

    def _apply_size(self, width: int, height: int):
        raise NotImplementedError

    def content_size(self):
        rect = self.boundingRect()
        return rect.width(), rect.height()


class MovablePixmapItem(_LayerMixin, QGraphicsPixmapItem if QGraphicsPixmapItem else object):
    def __init__(self, pixmap=None, layer_id: str = "", layer_name: str = "layer", movement_callback=None, resize_callback=None):
        require_pyside()
        super().__init__(pixmap)
        self.configure_layer(layer_id, layer_name, movement_callback=movement_callback, resize_callback=resize_callback)

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        self.paint_resize_handles(painter)

    def _current_pixmap(self):
        return self.pixmap()

    def _apply_size(self, width: int, height: int):
        source = self._resize_source_pixmap or self.pixmap()
        if source and not source.isNull():
            self.setPixmap(source.scaled(width, height, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation))


class PlaceholderLayerItem(_LayerMixin, QGraphicsRectItem if QGraphicsRectItem else object):
    def __init__(self, width: int = 1280, height: int = 720, layer_id: str = "", layer_name: str = "placeholder", movement_callback=None, resize_callback=None):
        require_pyside()
        super().__init__(QRectF(0, 0, width, height))
        self.configure_layer(layer_id, layer_name, movement_callback=movement_callback, resize_callback=resize_callback)
        self.setBrush(QBrush(QColor(32, 36, 42)))
        self.setPen(QPen(QColor(95, 110, 130), 2))

    def paint(self, painter, option, widget=None):
        super().paint(painter, option, widget)
        self.paint_resize_handles(painter)

    def _apply_size(self, width: int, height: int):
        self.setRect(QRectF(0, 0, width, height))

    def content_size(self):
        rect = self.rect()
        return rect.width(), rect.height()
