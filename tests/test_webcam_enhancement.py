import json

from rinovision.studio_composer.controller import StudioComposerController
from rinovision.studio_composer.webcam_enhancement import (
    apply_brightness_contrast,
    default_webcam_enhancement,
    mirror_frame,
    reset_webcam_enhancement,
)


def test_enhancement_module_imports_without_camera():
    defaults = default_webcam_enhancement()
    assert defaults["brightness"] == 0
    assert defaults["contrast"] == 1.0
    assert defaults["mirror"] is True


def test_default_enhancement_metadata_exists():
    controller = StudioComposerController("webcam-enhancement-default")
    webcam = controller.add_webcam_layer(enabled=True)
    enhancement = webcam.metadata["enhancement"]
    assert enhancement == default_webcam_enhancement()


def test_brightness_contrast_with_numpy_if_available():
    try:
        import numpy as np
    except ImportError:
        return
    frame = np.zeros((2, 2, 3), dtype=np.uint8)
    adjusted = apply_brightness_contrast(frame, brightness=20, contrast=1.0)
    assert adjusted.shape == frame.shape
    assert adjusted.max() >= 20


def test_mirror_frame_with_numpy_if_available():
    try:
        import numpy as np
    except ImportError:
        return
    frame = np.array([[[1, 1, 1], [2, 2, 2], [3, 3, 3]]], dtype=np.uint8)
    mirrored = mirror_frame(frame)
    assert mirrored[0, 0, 0] == 3


def test_mirror_flag_is_saved_in_layout_json():
    controller = StudioComposerController("webcam-enhancement-layout")
    webcam = controller.add_webcam_layer(enabled=True)
    webcam.metadata["enhancement"]["mirror"] = False
    path = controller.save_layout()
    payload = json.loads(path.read_text(encoding="utf-8"))
    layer = next(item for item in payload["layers"] if item["layer_type"] == "webcam")
    assert layer["metadata"]["enhancement"]["mirror"] is False


def test_reset_returns_default_values():
    metadata = {"enhancement": {"brightness": 50, "contrast": 2.0, "saturation": 0.5, "gamma": 1.4, "mirror": False}}
    reset = reset_webcam_enhancement(metadata)
    assert reset == default_webcam_enhancement()
    assert metadata["enhancement"] == default_webcam_enhancement()


def test_healthcheck_reports_webcam_enhancement():
    from scripts.rinovision_healthcheck import run_healthcheck

    report = run_healthcheck()
    assert report["studio_composer"]["webcam_enhancement_import"]["ok"] is True
