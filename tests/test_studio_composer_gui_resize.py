import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from rinovision.studio_composer.models import ComposerLayer
from rinovision.studio_composer.ui.studio_window import StudioComposerWindow


@pytest.fixture
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app
    for widget in app.topLevelWidgets():
        widget.close()
        widget.deleteLater()
    app.processEvents()


def _add_placeholder(window, layer):
    window.controller.scene.layers.append(layer)
    window.controller.scene.selected_layer_id = layer.id
    item = window.canvas.add_placeholder_layer(layer)
    item.setSelected(True)
    window.on_selection_changed()
    return item


def test_direct_resize_updates_model_and_inspector(qapp):
    window = StudioComposerWindow()
    layer = ComposerLayer(name="Resizable Image", layer_type="image", layer_slot=2, width=320, height=180)
    item = _add_placeholder(window, layer)

    assert item.resize_to(640, 360) is True

    assert layer.width == 640
    assert layer.height == 360
    assert float(window.inspector.labels["width"].text()) == 640
    assert float(window.inspector.labels["height"].text()) == 360


def test_direct_resize_preserves_independent_layers(qapp):
    window = StudioComposerWindow()
    first = ComposerLayer(name="First", layer_type="image", layer_slot=2, width=320, height=180)
    second = ComposerLayer(name="Second", layer_type="video", layer_slot=1, width=300, height=200)
    first_item = _add_placeholder(window, first)
    _add_placeholder(window, second)

    assert first_item.resize_to(500, 400) is True

    assert first.width == 500
    assert first.height == 400
    assert second.width == 300
    assert second.height == 200


def test_locked_layer_blocks_direct_resize(qapp):
    window = StudioComposerWindow()
    layer = ComposerLayer(name="Locked Resize", layer_type="image", layer_slot=2, width=320, height=180)
    item = _add_placeholder(window, layer)

    item.set_locked(True)

    assert item.resize_to(640, 360) is False
    assert layer.width == 320
    assert layer.height == 180


def test_locked_scene_blocks_direct_resize(qapp):
    window = StudioComposerWindow()
    layer = ComposerLayer(name="Scene Locked Resize", layer_type="video", layer_slot=2, width=320, height=180)
    item = _add_placeholder(window, layer)

    window.lock_layout()

    assert item.resize_to(640, 360) is False
    assert layer.width == 320
    assert layer.height == 180
