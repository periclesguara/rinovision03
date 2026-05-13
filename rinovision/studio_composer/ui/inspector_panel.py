try:
    from PySide6.QtWidgets import QFormLayout, QLabel, QWidget
    _IMPORT_ERROR = None
except ImportError as exc:
    QFormLayout = QLabel = QWidget = None
    _IMPORT_ERROR = exc

from rinovision.studio_composer.ui.layer_items import require_pyside


class InspectorPanel(QWidget if QWidget else object):
    def __init__(self, parent=None):
        require_pyside()
        super().__init__(parent)
        self.labels = {}
        layout = QFormLayout(self)
        for key in ("layer_id", "layer_name", "layer_type", "x", "y", "width", "height", "scale", "z_index", "visible", "locked"):
            label = QLabel("-")
            self.labels[key] = label
            layout.addRow(key.replace("_", " ").title(), label)

    def update_values(self, values: dict):
        for key, label in self.labels.items():
            label.setText(str(values.get(key, "-")))
