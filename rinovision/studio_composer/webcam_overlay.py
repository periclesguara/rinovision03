from rinovision.capture.webcam import WebcamPreviewController
from rinovision.studio_composer.webcam_enhancement import default_webcam_enhancement


class WebcamOverlayController:
    def __init__(self, camera_id: int = 0):
        self.preview = WebcamPreviewController(camera_id=camera_id)

    def start_preview(self) -> dict:
        return self.preview.start()

    def read_frame(self):
        return self.preview.read_frame()

    def stop_preview(self) -> dict:
        return self.preview.stop()

    def status(self) -> dict:
        return self.preview.get_status()


def webcam_layer_metadata(camera_id: int = 0, mode: str = "free_floating", enabled: bool = False) -> dict:
    if mode not in {"inside_base", "free_floating"}:
        raise ValueError("webcam mode must be inside_base or free_floating")
    return {
        "camera_id": camera_id,
        "mode": mode,
        "enabled": enabled,
        "enhancement": default_webcam_enhancement(),
    }
