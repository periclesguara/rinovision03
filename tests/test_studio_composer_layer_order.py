from rinovision.studio_composer.controller import StudioComposerController
from rinovision.studio_composer.ui.canvas_view import StudioCanvasView


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


def test_canvas_geometry_sync_keeps_base_size_separate_from_scale():
    controller = StudioComposerController("geometry-scene")
    layer = controller.add_webcam_layer(enabled=False)
    layer.width = 320
    layer.height = 240
    layer.scale = 2.0

    class Rect:
        def width(self):
            return 320

        def height(self):
            return 240

    class FakeItem:
        def boundingRect(self):
            return Rect()

        def x(self):
            return 10

        def y(self):
            return 20

        def scale(self):
            return 2.0

        def rotation(self):
            return 0

        def zValue(self):
            return 99

        def isVisible(self):
            return True

    canvas = StudioCanvasView.__new__(StudioCanvasView)
    canvas.items_by_layer_id = {layer.id: FakeItem()}
    canvas.sync_layer_geometry(layer)

    assert layer.width == 320
    assert layer.height == 240
    assert layer.scale == 2.0


def test_live_webcam_geometry_sync_does_not_mutate_frame_size():
    controller = StudioComposerController("stable-webcam-scene")
    layer = controller.add_webcam_layer(enabled=True)
    layer.width = 320
    layer.height = 240
    layer.metadata["frame_width"] = 320
    layer.metadata["frame_height"] = 240
    layer.metadata["stable_frame_size"] = True

    class Rect:
        def width(self):
            return 999

        def height(self):
            return 777

    class FakeItem:
        def boundingRect(self):
            return Rect()

        def x(self):
            return 15

        def y(self):
            return 25

        def scale(self):
            return 1.25

        def rotation(self):
            return 0

        def zValue(self):
            return 99

        def isVisible(self):
            return True

    canvas = StudioCanvasView.__new__(StudioCanvasView)
    canvas.items_by_layer_id = {layer.id: FakeItem()}
    canvas.sync_layer_geometry(layer)

    assert layer.x == 15
    assert layer.y == 25
    assert layer.width == 320
    assert layer.height == 240
    assert layer.scale == 1.25
