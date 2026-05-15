import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from rinovision.studio_composer.models import ComposerLayer
from rinovision.studio_composer.ui.studio_window import StudioComposerWindow


@pytest.fixture
def qapp():
    return QApplication.instance() or QApplication([])


def _add_placeholder(window, layer):
    window.controller.scene.layers.append(layer)
    window.controller.scene.selected_layer_id = layer.id
    item = window.canvas.add_placeholder_layer(layer)
    item.setSelected(True)
    window.on_selection_changed()
    return item


def _set_combo_to_slot(combo, slot):
    index = combo.findData(slot)
    assert index >= 0
    combo.setCurrentIndex(index)


def test_gui_adds_image_layer_with_real_slot_z_value(qapp):
    window = StudioComposerWindow()
    layer = ComposerLayer(name="Image Slot 2", layer_type="image", layer_slot=2, width=320, height=180)

    item = _add_placeholder(window, layer)

    assert item.zValue() == layer.computed_z_index
    assert window.inspector.labels["layer_slot"].text() == "2"


def test_gui_adds_video_layer_with_real_slot_z_value(qapp):
    window = StudioComposerWindow()
    layer = ComposerLayer(name="Video Slot 3", layer_type="video", layer_slot=3, width=320, height=180)

    item = _add_placeholder(window, layer)

    assert item.zValue() == layer.computed_z_index
    assert layer.computed_z_index < 3000


def test_selected_slot_combo_updates_model_and_graphics_z_without_moving(qapp):
    window = StudioComposerWindow()
    layer = ComposerLayer(name="Movable Slot", layer_type="image", layer_slot=2, x=111, y=222, width=320, height=180)
    item = _add_placeholder(window, layer)

    _set_combo_to_slot(window.selected_layer_slot_combo, 1)

    assert layer.layer_slot == 1
    assert layer.computed_z_index >= 4000
    assert item.zValue() == layer.computed_z_index
    assert layer.x == 111
    assert layer.y == 222
    assert window.inspector.labels["layer_slot"].text() == "1"


def test_locked_scene_blocks_selected_slot_change(qapp):
    window = StudioComposerWindow()
    layer = ComposerLayer(name="Locked Slot", layer_type="image", layer_slot=2, width=320, height=180)
    item = _add_placeholder(window, layer)
    original_z = item.zValue()

    window.lock_layout()
    _set_combo_to_slot(window.selected_layer_slot_combo, 1)

    assert layer.layer_slot == 2
    assert item.zValue() == original_z
    assert window.inspector.labels["layer_slot"].text() == "2"
