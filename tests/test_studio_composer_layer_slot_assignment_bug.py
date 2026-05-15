import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from rinovision.studio_composer.controller import StudioComposerController
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


def _media_file(tmp_path, name):
    path = tmp_path / name
    path.write_bytes(b"placeholder")
    return path


def _set_combo_to_slot(combo, slot):
    index = combo.findData(slot)
    assert index >= 0
    combo.setCurrentIndex(index)


def test_image_layer_1_appears_above_webcam_layer_2(qapp, tmp_path):
    controller = StudioComposerController("assignment-bug")
    canvas = StudioCanvasView()
    webcam = controller.add_webcam_layer(camera_id=0, layer_slot=2)
    image = controller.add_image_layer(_media_file(tmp_path, "foreground.png"), layer_slot=1)

    webcam_item = canvas.add_placeholder_layer(webcam)
    image_item = canvas.add_placeholder_layer(image)
    canvas.refresh_all_z_values_from_model(controller.scene.layers)

    assert webcam.layer_slot == 2
    assert image.layer_slot == 1
    assert image.computed_z_index > webcam.computed_z_index
    assert image_item.zValue() > webcam_item.zValue()


def test_user_selected_slot_not_overwritten_by_defaults(qapp, tmp_path):
    controller = StudioComposerController("assignment-defaults")
    webcam = controller.add_webcam_layer(camera_id=0, layer_slot=2)
    image = controller.add_image_layer(_media_file(tmp_path, "image.png"), layer_slot=1)
    video = controller.add_video_layer(_media_file(tmp_path, "video.mp4"), layer_slot=3)

    assert webcam.layer_slot == 2
    assert image.layer_slot == 1
    assert video.layer_slot == 3


def test_changing_existing_layer_slot_updates_qgraphics_z_value(qapp, tmp_path):
    controller = StudioComposerController("assignment-change")
    canvas = StudioCanvasView()
    image = controller.add_image_layer(_media_file(tmp_path, "image.png"), layer_slot=2)
    image_item = canvas.add_placeholder_layer(image)
    old_x = image.x
    old_y = image.y

    controller.move_layer_to_slot(image.id, 1)
    canvas.sync_item_z_order(image)

    assert image.layer_slot == 1
    assert image.x == old_x
    assert image.y == old_y
    assert image_item.zValue() == image.computed_z_index


def test_real_ui_combo_case_image_layer_1_above_webcam_layer_2(qapp, tmp_path):
    window = StudioComposerWindow()
    _set_combo_to_slot(window.webcam_layer_slot_combo, 2)
    webcam = window.add_webcam_layer_to_selected_slot(enabled=False)
    webcam_item = window.canvas.add_placeholder_layer(webcam)
    window.canvas.sync_item_z_order(webcam)

    _set_combo_to_slot(window.image_layer_slot_combo, 1)
    image = window.add_image_path_to_selected_slot(_media_file(tmp_path, "foreground.png"))
    image_item = window.canvas.get_item_by_layer_id(image.id)

    assert webcam.layer_slot == 2
    assert image.layer_slot == 1
    assert image.computed_z_index > webcam.computed_z_index
    assert image_item.zValue() > webcam_item.zValue()
