import subprocess
import sys

from rinovision.studio_composer import create_demo_multilayer
from rinovision.studio_composer.controller import StudioComposerController


def _media_file(tmp_path, name):
    path = tmp_path / name
    path.write_bytes(b"placeholder")
    return path


def test_multiple_image_layers_can_be_added(tmp_path):
    controller = StudioComposerController("multi-images")
    first = controller.add_image_layer(_media_file(tmp_path, "one.png"))
    second = controller.add_image_layer(_media_file(tmp_path, "two.jpg"))
    assert first.layer_type == "image"
    assert second.layer_type == "image"
    assert first.id != second.id
    assert len(controller.scene.layers) == 2


def test_multiple_video_layers_can_be_added(tmp_path):
    controller = StudioComposerController("multi-videos")
    first = controller.add_video_layer(_media_file(tmp_path, "one.mp4"))
    second = controller.add_video_layer(_media_file(tmp_path, "two.webm"))
    assert first.layer_type == "video"
    assert second.layer_type == "video"
    assert first.id != second.id


def test_image_video_and_webcam_layers_coexist(tmp_path):
    controller = StudioComposerController("mixed-scene")
    controller.add_image_layer(_media_file(tmp_path, "image.webp"))
    controller.add_video_layer(_media_file(tmp_path, "video.mkv"))
    webcam = controller.add_webcam_layer(enabled=False)
    layer_types = {layer.layer_type for layer in controller.scene.layers}
    assert {"image", "video", "webcam"}.issubset(layer_types)
    assert webcam.metadata["enabled"] is False


def test_lock_and_unlock_scene_affects_all_layers(tmp_path):
    controller = StudioComposerController("lock-scene")
    controller.add_image_layer(_media_file(tmp_path, "image.png"))
    controller.add_video_layer(_media_file(tmp_path, "video.mp4"))
    controller.add_webcam_layer(enabled=False)
    controller.lock_scene()
    assert controller.scene.locked is True
    assert all(layer.locked for layer in controller.scene.layers)
    controller.unlock_scene()
    assert controller.scene.locked is False
    assert all(not layer.locked for layer in controller.scene.layers)


def test_layout_json_persists_all_layers(tmp_path):
    controller = StudioComposerController("persist-scene")
    controller.add_image_layer(_media_file(tmp_path, "image.png"))
    controller.add_video_layer(_media_file(tmp_path, "video.mp4"))
    controller.add_webcam_layer(enabled=False)
    path = controller.lock_scene()
    payload = path.read_text(encoding="utf-8")
    assert '"layers"' in payload
    assert '"layer_type": "image"' in payload
    assert '"layer_type": "video"' in payload
    assert '"layer_type": "webcam"' in payload


def test_demo_multilayer_command_works_without_gui():
    completed = subprocess.run(
        [sys.executable, "main.py", "--studio-composer-demo-multilayer"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert "Studio Composer multilayer demo complete" in completed.stdout
    assert "recording: not enabled" in completed.stdout


def test_create_demo_multilayer_has_three_layers():
    result = create_demo_multilayer("demo-multilayer-test")
    assert result["layer_count"] == 3
    assert result["layout"]["locked"] is True
