import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from rinovision.studio_composer.ui.studio_window import StudioComposerWindow


@pytest.fixture
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app
    for widget in app.topLevelWidgets():
        widget.close()
        widget.deleteLater()
    app.processEvents()


def _media_file(tmp_path, name):
    path = tmp_path / name
    path.write_bytes(b"placeholder")
    return path


def _set_combo_to_slot(combo, slot):
    index = combo.findData(slot)
    assert index >= 0
    combo.setCurrentIndex(index)


def test_image_upload_uses_selected_layer_slot_and_graphics_z(qapp, tmp_path):
    window = StudioComposerWindow()
    _set_combo_to_slot(window.image_layer_slot_combo, 1)

    layer = window.add_image_path_to_selected_slot(_media_file(tmp_path, "image.png"))
    item = window.canvas.get_item_by_layer_id(layer.id)

    assert layer.layer_slot == 1
    assert layer.computed_z_index >= 4000
    assert item.zValue() == layer.computed_z_index


def test_video_upload_uses_selected_layer_slot_and_graphics_z(qapp, tmp_path):
    window = StudioComposerWindow()
    _set_combo_to_slot(window.video_layer_slot_combo, 2)

    layer = window.add_video_path_to_selected_slot(_media_file(tmp_path, "video.mp4"))
    item = window.canvas.get_item_by_layer_id(layer.id)

    assert layer.layer_slot == 2
    assert 3000 <= layer.computed_z_index < 4000
    assert item.zValue() == layer.computed_z_index


def test_webcam_layer_uses_selected_layer_slot_without_camera_access(qapp):
    window = StudioComposerWindow()
    _set_combo_to_slot(window.webcam_layer_slot_combo, 1)

    layer = window.add_webcam_layer_to_selected_slot(enabled=False)

    assert layer.layer_slot == 1
    assert layer.computed_z_index >= 4000


def test_selected_layer_slot_change_updates_model_z_and_item_without_moving(qapp, tmp_path):
    window = StudioComposerWindow()
    _set_combo_to_slot(window.image_layer_slot_combo, 2)
    layer = window.add_image_path_to_selected_slot(_media_file(tmp_path, "slot-change.png"))
    item = window.canvas.get_item_by_layer_id(layer.id)
    original_x = layer.x
    original_y = layer.y

    _set_combo_to_slot(window.selected_layer_slot_combo, 1)

    assert layer.layer_slot == 1
    assert layer.computed_z_index >= 4000
    assert item.zValue() == layer.computed_z_index
    assert layer.x == original_x
    assert layer.y == original_y
    assert window.inspector.labels["layer_slot"].text() == "1"


def test_locked_scene_blocks_layer_slot_change_and_reverts_combo(qapp, tmp_path):
    window = StudioComposerWindow()
    layer = window.add_image_path_to_selected_slot(_media_file(tmp_path, "locked-scene.png"))
    item = window.canvas.get_item_by_layer_id(layer.id)
    original_slot = layer.layer_slot
    original_z = item.zValue()

    window.lock_layout()
    _set_combo_to_slot(window.selected_layer_slot_combo, 1)

    assert layer.layer_slot == original_slot
    assert item.zValue() == original_z
    assert window.inspector.labels["layer_slot"].text() == str(original_slot)


def test_locked_layer_blocks_layer_slot_change_and_reverts_combo(qapp, tmp_path):
    window = StudioComposerWindow()
    layer = window.add_image_path_to_selected_slot(_media_file(tmp_path, "locked-layer.png"))
    item = window.canvas.get_item_by_layer_id(layer.id)
    original_slot = layer.layer_slot
    original_z = item.zValue()
    layer.locked = True
    item.set_locked(True)

    _set_combo_to_slot(window.selected_layer_slot_combo, 1)

    assert layer.layer_slot == original_slot
    assert item.zValue() == original_z
    assert window.inspector.labels["layer_slot"].text() == str(original_slot)


def test_layer_panel_grouping_reflects_real_model_state(qapp, tmp_path):
    window = StudioComposerWindow()
    _set_combo_to_slot(window.image_layer_slot_combo, 3)
    image = window.add_image_path_to_selected_slot(_media_file(tmp_path, "background.png"))
    _set_combo_to_slot(window.video_layer_slot_combo, 2)
    video = window.add_video_path_to_selected_slot(_media_file(tmp_path, "main.mp4"))

    text = window.layer_panel.text()

    assert "Layer 1" in text
    assert "Layer 2" in text and video.name in text
    assert "Layer 3" in text and image.name in text
    assert "Layer 4" in text
