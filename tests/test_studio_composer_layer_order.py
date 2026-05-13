from rinovision.studio_composer.controller import StudioComposerController


def _media_file(tmp_path, name):
    path = tmp_path / name
    path.write_bytes(b"placeholder")
    return path


def test_z_index_ordering_and_forward_backward(tmp_path):
    controller = StudioComposerController("order-scene")
    first = controller.add_image_layer(_media_file(tmp_path, "first.png"))
    second = controller.add_image_layer(_media_file(tmp_path, "second.png"))
    assert first.z_index < second.z_index

    controller.bring_forward(first.id)
    assert first.z_index > second.z_index

    controller.send_backward(first.id)
    assert first.z_index < second.z_index


def test_set_layer_z_index(tmp_path):
    controller = StudioComposerController("z-scene")
    layer = controller.add_image_layer(_media_file(tmp_path, "image.png"))
    controller.set_layer_z_index(layer.id, 42)
    assert layer.z_index == 42


def test_layer_visibility_toggle(tmp_path):
    controller = StudioComposerController("visibility-scene")
    layer = controller.add_image_layer(_media_file(tmp_path, "image.png"))
    controller.toggle_layer_visibility(layer.id)
    assert layer.visible is False
    controller.toggle_layer_visibility(layer.id)
    assert layer.visible is True
