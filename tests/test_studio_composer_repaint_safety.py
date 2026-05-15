import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QGraphicsItem

from rinovision.studio_composer.models import ComposerLayer
from rinovision.studio_composer.ui.canvas_view import StudioCanvasView
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


def test_canvas_uses_full_viewport_repaint_and_no_view_cache(qapp):
    canvas = StudioCanvasView()

    assert canvas.viewportUpdateMode() == canvas.ViewportUpdateMode.FullViewportUpdate
    assert canvas.cacheMode() == canvas.CacheModeFlag.CacheNone


def test_layer_item_bounding_rect_includes_resize_handle_padding(qapp):
    window = StudioComposerWindow()
    layer = ComposerLayer(name="Padded", layer_type="image", width=320, height=180)
    item = _add_placeholder(window, layer)

    content = item.content_rect()
    bounds = item.boundingRect()

    assert bounds.width() > content.width()
    assert bounds.height() > content.height()
    assert bounds.left() < content.left()
    assert bounds.top() < content.top()


def test_layer_item_cache_is_disabled_for_movable_resizable_items(qapp):
    window = StudioComposerWindow()
    layer = ComposerLayer(name="No Cache", layer_type="video", width=320, height=180)
    item = _add_placeholder(window, layer)

    assert item.cacheMode() == QGraphicsItem.CacheMode.NoCache


def test_resize_repaint_path_updates_size_without_crashing(qapp):
    window = StudioComposerWindow()
    layer = ComposerLayer(name="Resize Repaint", layer_type="image", width=320, height=180)
    item = _add_placeholder(window, layer)

    assert item.resize_to(640, 360) is True

    assert layer.width == 640
    assert layer.height == 360


def test_move_repaint_path_updates_position_without_crashing(qapp):
    window = StudioComposerWindow()
    layer = ComposerLayer(name="Move Repaint", layer_type="image", width=320, height=180)
    item = _add_placeholder(window, layer)

    item.setPos(123, 234)

    assert layer.x == 123
    assert layer.y == 234


def test_selection_toggle_repaint_path_does_not_crash(qapp):
    window = StudioComposerWindow()
    layer = ComposerLayer(name="Selection Repaint", layer_type="image", width=320, height=180)
    item = _add_placeholder(window, layer)

    item.setSelected(False)
    item.setSelected(True)
    window.on_selection_changed()

    assert window.inspector.labels["layer_id"].text() == layer.id
