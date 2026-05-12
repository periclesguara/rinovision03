class WebcamCaptureAdapter:
    def __init__(self):
        self.legacy_class = get_legacy_webcam_manager()
        self.available = not isinstance(self.legacy_class, dict)

    def create_legacy(self, *args, **kwargs):
        if not self.available:
            return self.legacy_class
        return self.legacy_class(*args, **kwargs)

    def status(self) -> dict:
        if self.available:
            return {"available": True, "backend": "managers.webcam_manager.WebcamManager"}
        return {"available": False, **self.legacy_class}


def get_legacy_webcam_manager():
    try:
        from managers.webcam_manager import WebcamManager

        return WebcamManager
    except Exception as exc:
        return {"import_error": str(exc)}
