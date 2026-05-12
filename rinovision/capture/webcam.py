import importlib.util


WEBCAM_DEPENDENCIES = {
    "cv2": "opencv-python",
    "numpy": "numpy",
    "mediapipe": "mediapipe",
}


def _dependency_available(module_name: str) -> bool:
    try:
        return importlib.util.find_spec(module_name) is not None
    except (ImportError, ValueError):
        return False


def webcam_missing_dependencies() -> list[str]:
    return [
        package_name
        for module_name, package_name in WEBCAM_DEPENDENCIES.items()
        if not _dependency_available(module_name)
    ]


class WebcamCaptureAdapter:
    def __init__(self):
        self.legacy_class = get_legacy_webcam_manager()
        self.missing_dependencies = webcam_missing_dependencies()
        self.available = not isinstance(self.legacy_class, dict) and not self.missing_dependencies

    def create_legacy(self, *args, **kwargs):
        if not self.available:
            return self.status()
        return self.legacy_class(*args, **kwargs)

    def status(self) -> dict:
        if isinstance(self.legacy_class, dict):
            return {
                "available": False,
                "missing_dependencies": self.missing_dependencies,
                "message": "Legacy webcam manager is not importable.",
                **self.legacy_class,
            }
        if self.missing_dependencies:
            return {
                "available": False,
                "backend": "managers.webcam_manager.WebcamManager",
                "missing_dependencies": self.missing_dependencies,
                "message": "Install optional webcam dependencies before creating a legacy webcam instance.",
            }
        return {
            "available": True,
            "backend": "managers.webcam_manager.WebcamManager",
            "missing_dependencies": [],
            "message": "Legacy webcam manager import is safe. Camera opens only when create_legacy() instantiates it.",
        }


def get_legacy_webcam_manager():
    try:
        from managers.webcam_manager import WebcamManager

        return WebcamManager
    except Exception as exc:
        return {"import_error": str(exc)}
