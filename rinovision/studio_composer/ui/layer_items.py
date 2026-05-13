try:
    from PySide6.QtCore import QRectF
    from PySide6.QtGui import QBrush, QColor, QPen
    from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsRectItem
    _IMPORT_ERROR = None
except ImportError as exc:
    QRectF = QBrush = QColor = QPen = QGraphicsPixmapItem = QGraphicsRectItem = None
    _IMPORT_ERROR = exc


def require_pyside():
    if _IMPORT_ERROR:
        raise RuntimeError(f"PySide6 is required for Studio Composer UI: {_IMPORT_ERROR}") from _IMPORT_ERROR


class _LayerMixin:
    def configure_layer(self, layer_id: str, layer_name: str, movement_callback=None):
        self.layer_id = layer_id
        self.layer_name = layer_name
        self.locked = False
        self.movement_callback = movement_callback
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(self.GraphicsItemFlag.ItemSendsGeometryChanges, True)

    def set_locked(self, locked: bool):
        self.locked = locked
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable, not locked)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, not locked)

    def itemChange(self, change, value):
        if change == self.GraphicsItemChange.ItemPositionHasChanged and self.movement_callback and not self.locked:
            self.movement_callback(self.layer_id, value.x(), value.y())
        return super().itemChange(change, value)


class MovablePixmapItem(_LayerMixin, QGraphicsPixmapItem if QGraphicsPixmapItem else object):
    def __init__(self, pixmap=None, layer_id: str = "", layer_name: str = "layer", movement_callback=None):
        require_pyside()
        super().__init__(pixmap)
        self.configure_layer(layer_id, layer_name, movement_callback=movement_callback)


class PlaceholderLayerItem(_LayerMixin, QGraphicsRectItem if QGraphicsRectItem else object):
    def __init__(self, width: int = 1280, height: int = 720, layer_id: str = "", layer_name: str = "placeholder", movement_callback=None):
        require_pyside()
        super().__init__(QRectF(0, 0, width, height))
        self.configure_layer(layer_id, layer_name, movement_callback=movement_callback)
        self.setBrush(QBrush(QColor(32, 36, 42)))
        self.setPen(QPen(QColor(95, 110, 130), 2))
