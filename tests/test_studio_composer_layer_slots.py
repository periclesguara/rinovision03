import json

import pytest

from rinovision.studio_composer.controller import StudioComposerController


def _media_file(tmp_path, name):
    path = tmp_path / name
    path.write_bytes(b"placeholder")
    return path


def test_default_scene_creates_four_layer_slots():
    controller = StudioComposerController("slots-default")
    assert [slot.slot_number for slot in controller.scene.layer_slots] == [1, 2, 3, 4]


def test_slot_z_order_is_foreground_to_background():
    controller = StudioComposerController("slots-z-order")
    assert controller.compute_z_index(1) > controller.compute_z_index(2)
    assert controller.compute_z_index(2) > controller.compute_z_index(3)
    assert controller.compute_z_index(3) > controller.compute_z_index(4)


def test_image_can_be_added_to_layer_1_and_2(tmp_path):
    controller = StudioComposerController("image-slots")
    layer_1 = controller.add_image_layer(_media_file(tmp_path, "one.png"), layer_slot=1)
    layer_2 = controller.add_image_layer(_media_file(tmp_path, "two.png"), layer_slot=2)
    assert layer_1.layer_slot == 1
    assert layer_1.computed_z_index >= 4000
    assert layer_2.layer_slot == 2
    assert layer_2.computed_z_index >= 3000


def test_video_can_be_added_to_layer_3(tmp_path):
    controller = StudioComposerController("video-slot")
    video = controller.add_video_layer(_media_file(tmp_path, "video.mp4"), layer_slot=3)
    assert video.layer_slot == 3
    assert video.computed_z_index >= 2000


def test_webcam_defaults_to_layer_1_and_can_move_to_layer_2():
    controller = StudioComposerController("webcam-slot")
    webcam = controller.add_webcam_layer(enabled=True)
    assert webcam.layer_slot == 1
    assert webcam.computed_z_index == 4000
    controller.move_layer_to_slot(webcam.id, 2)
    assert webcam.layer_slot == 2
    assert webcam.computed_z_index == 3000


def test_moving_item_to_another_slot_recomputes_z_index(tmp_path):
    controller = StudioComposerController("move-slot")
    image = controller.add_image_layer(_media_file(tmp_path, "image.png"), layer_slot=4)
    controller.move_layer(image.id, 640, 120)
    assert image.computed_z_index >= 1000
    controller.move_layer_to_slot(image.id, 1)
    assert image.layer_slot == 1
    assert image.computed_z_index >= 4000
    assert image.x == 640
    assert image.y == 120


def test_layer_slot_controls_depth_not_canvas_position(tmp_path):
    controller = StudioComposerController("slot-not-quadrant")
    image = controller.add_image_layer(_media_file(tmp_path, "image.png"), layer_slot=4)
    controller.move_layer(image.id, 1200, 20)
    controller.move_layer_to_slot(image.id, 1)

    assert image.layer_slot == 1
    assert image.x == 1200
    assert image.y == 20


def test_layout_json_preserves_layer_slot_and_computed_z_index(tmp_path):
    controller = StudioComposerController("slot-json")
    video = controller.add_video_layer(_media_file(tmp_path, "video.mp4"), layer_slot=3)
    path = controller.save_layout()
    payload = json.loads(path.read_text(encoding="utf-8"))
    layer = next(item for item in payload["layers"] if item["id"] == video.id)
    assert layer["layer_slot"] == 3
    assert layer["computed_z_index"] == video.computed_z_index
    assert payload["layer_slots"][0]["slot_number"] == 1


def test_empty_layers_are_allowed_by_default():
    controller = StudioComposerController("empty-slots")
    grouped = controller.get_scene_layers_grouped_by_slot()
    assert grouped[3] == []
    assert grouped[4] == []


def test_invalid_layer_slot_is_rejected(tmp_path):
    controller = StudioComposerController("invalid-slot")
    with pytest.raises(ValueError):
        controller.add_image_layer(_media_file(tmp_path, "image.png"), layer_slot=5)


def test_bring_forward_and_send_backward_within_slot(tmp_path):
    controller = StudioComposerController("within-slot")
    first = controller.add_image_layer(_media_file(tmp_path, "first.png"), layer_slot=2)
    second = controller.add_image_layer(_media_file(tmp_path, "second.png"), layer_slot=2)
    controller.bring_forward_within_slot(first.id)
    assert first.layer_slot == second.layer_slot
    assert first.computed_z_index > second.computed_z_index
    controller.send_backward_within_slot(first.id)
    assert first.computed_z_index < second.computed_z_index
