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
    def configure_layer(self, layer_id: str, layer_name: str):
        self.layer_id = layer_id
        self.layer_name = layer_name
        self.locked = False
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(self.GraphicsItemFlag.ItemSendsGeometryChanges, True)

    def set_locked(self, locked: bool):
        self.locked = locked
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable, not locked)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, not locked)

    def wheelEvent(self, event):
        if self.locked:
            event.ignore()
            return
        factor = 1.05 if event.delta() > 0 else 0.95
        self.setScale(max(0.05, min(10.0, self.scale() * factor)))
        event.accept()


class MovablePixmapItem(_LayerMixin, QGraphicsPixmapItem if QGraphicsPixmapItem else object):
    def __init__(self, pixmap=None, layer_id: str = "", layer_name: str = "layer"):
        require_pyside()
        super().__init__(pixmap)
        self.configure_layer(layer_id, layer_name)


class PlaceholderLayerItem(_LayerMixin, QGraphicsRectItem if QGraphicsRectItem else object):
    def __init__(self, width: int = 1280, height: int = 720, layer_id: str = "", layer_name: str = "placeholder"):
        require_pyside()
        super().__init__(QRectF(0, 0, width, height))
        self.configure_layer(layer_id, layer_name)
        self.setBrush(QBrush(QColor(32, 36, 42)))
        self.setPen(QPen(QColor(95, 110, 130), 2))
