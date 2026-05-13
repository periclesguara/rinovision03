import json

import pytest

from rinovision.studio_composer.controller import StudioComposerController


def _media_file(tmp_path, name):
    path = tmp_path / name
    path.write_bytes(b"placeholder")
    return path


def test_image_layer_movement_updates_xy(tmp_path):
    controller = StudioComposerController("move-image")
    image = controller.add_image_layer(_media_file(tmp_path, "image.png"))

    controller.move_layer(image.id, 123, 234)

    assert image.x == 123
    assert image.y == 234
    assert "updated_at" in image.metadata


def test_video_layer_movement_updates_xy(tmp_path):
    controller = StudioComposerController("move-video")
    video = controller.add_video_layer(_media_file(tmp_path, "video.mp4"))

    controller.move_layer(video.id, 77, 88)

    assert video.x == 77
    assert video.y == 88


def test_webcam_layer_movement_updates_xy():
    controller = StudioComposerController("move-webcam")
    webcam = controller.add_webcam_layer(enabled=True)

    controller.move_layer(webcam.id, 320, 180)

    assert webcam.x == 320
    assert webcam.y == 180


def test_moving_one_layer_does_not_move_another(tmp_path):
    controller = StudioComposerController("independent-layers")
    first = controller.add_image_layer(_media_file(tmp_path, "first.png"))
    second = controller.add_image_layer(_media_file(tmp_path, "second.png"))

    controller.move_layer(first.id, 11, 22)

    assert first.x == 11
    assert first.y == 22
    assert second.x == 100
    assert second.y == 80


def test_locked_layer_cannot_move(tmp_path):
    controller = StudioComposerController("locked-layer")
    image = controller.add_image_layer(_media_file(tmp_path, "image.png"))
    controller.lock_layer(image.id)

    with pytest.raises(ValueError):
        controller.move_layer(image.id, 1, 2)


def test_globally_locked_scene_prevents_movement(tmp_path):
    controller = StudioComposerController("locked-scene")
    image = controller.add_image_layer(_media_file(tmp_path, "image.png"))
    controller.lock_scene()

    with pytest.raises(ValueError):
        controller.move_layer(image.id, 1, 2)


def test_unlock_restores_movement(tmp_path):
    controller = StudioComposerController("unlock-movement")
    image = controller.add_image_layer(_media_file(tmp_path, "image.png"))
    controller.lock_scene()
    controller.unlock_scene()

    controller.move_layer(image.id, 55, 66)

    assert image.x == 55
    assert image.y == 66


def test_saved_layout_preserves_moved_xy_values(tmp_path):
    controller = StudioComposerController("persist-movement")
    image = controller.add_image_layer(_media_file(tmp_path, "image.png"))
    video = controller.add_video_layer(_media_file(tmp_path, "video.mp4"))
    webcam = controller.add_webcam_layer(enabled=True)
    controller.move_layer(image.id, 10, 20)
    controller.move_layer(video.id, 30, 40)
    controller.move_layer(webcam.id, 50, 60)

    path = controller.save_layout()
    payload = json.loads(path.read_text(encoding="utf-8"))
    layers = {layer["id"]: layer for layer in payload["layers"]}

    assert layers[image.id]["x"] == 10
    assert layers[image.id]["y"] == 20
    assert layers[video.id]["x"] == 30
    assert layers[video.id]["y"] == 40
    assert layers[webcam.id]["x"] == 50
    assert layers[webcam.id]["y"] == 60
