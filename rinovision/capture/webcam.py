import importlib.util
import contextlib
import os


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


def check_webcam_dependencies() -> dict:
    missing = webcam_missing_dependencies()
    cv2_available = _dependency_available("cv2")
    if not cv2_available:
        return {
            "available": False,
            "missing_dependencies": ["opencv-python"],
            "optional_missing_dependencies": [
                package for module, package in WEBCAM_DEPENDENCIES.items() if module != "cv2" and not _dependency_available(module)
            ],
            "message": "OpenCV is required for webcam preview. Install with: pip install opencv-python",
        }
    optional_missing = [package for module, package in WEBCAM_DEPENDENCIES.items() if module != "cv2" and not _dependency_available(module)]
    return {
        "available": True,
        "missing_dependencies": [],
        "optional_missing_dependencies": optional_missing,
        "message": "Webcam preview dependencies are available." if not optional_missing else "Webcam preview is available; optional effects dependencies are missing.",
    }


def _import_cv2():
    try:
        import cv2
    except ImportError:
        return None
    return cv2


@contextlib.contextmanager
def _suppress_native_stderr():
    fd = 2
    saved_fd = os.dup(fd)
    try:
        with open(os.devnull, "w") as devnull:
            os.dup2(devnull.fileno(), fd)
            yield
    finally:
        os.dup2(saved_fd, fd)
        os.close(saved_fd)


def probe_webcams(max_devices: int = 5) -> list[dict]:
    cv2 = _import_cv2()
    if cv2 is None:
        return [
            {
                "camera_id": None,
                "available": False,
                "missing_dependencies": ["opencv-python"],
                "message": "OpenCV is missing. Install with: pip install opencv-python",
            }
        ]

    results = []
    for camera_id in range(max_devices):
        cap = None
        try:
            with _suppress_native_stderr():
                cap = cv2.VideoCapture(camera_id)
            available = bool(cap and cap.isOpened())
            item = {"camera_id": camera_id, "available": available}
            if available:
                item.update(
                    {
                        "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0),
                        "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0),
                        "fps": float(cap.get(cv2.CAP_PROP_FPS) or 0),
                    }
                )
            results.append(item)
        except Exception as exc:
            results.append({"camera_id": camera_id, "available": False, "error": str(exc)})
        finally:
            if cap is not None:
                cap.release()
    return results


class WebcamPreviewController:
    def __init__(self, camera_id: int = 0):
        self.camera_id = camera_id
        self._cv2 = None
        self._cap = None
        self._running = False
        self._last_error = ""

    def start(self) -> dict:
        if self._running and self._cap is not None:
            return self.get_status()

        cv2 = _import_cv2()
        if cv2 is None:
            self._last_error = "OpenCV is missing. Install with: pip install opencv-python"
            return {"ok": False, "camera_id": self.camera_id, "error": self._last_error, "missing_dependencies": ["opencv-python"]}

        self._cv2 = cv2
        try:
            self._cap = cv2.VideoCapture(self.camera_id)
            if not self._cap or not self._cap.isOpened():
                self._last_error = "Could not open camera"
                self.stop()
                return {"ok": False, "camera_id": self.camera_id, "error": self._last_error}
            self._running = True
            self._last_error = ""
            return {"ok": True, "camera_id": self.camera_id, "running": True}
        except Exception as exc:
            self._last_error = str(exc)
            self.stop()
            return {"ok": False, "camera_id": self.camera_id, "error": self._last_error}

    def read_frame(self):
        if not self._running or self._cap is None:
            return None
        ok, frame = self._cap.read()
        if not ok:
            self._last_error = "Could not read frame"
            return None
        return frame

    def stop(self) -> dict:
        cap = self._cap
        self._cap = None
        self._running = False
        if cap is not None:
            try:
                cap.release()
            except Exception as exc:
                self._last_error = str(exc)
                return {"ok": False, "camera_id": self.camera_id, "running": False, "error": self._last_error}
        return {"ok": True, "camera_id": self.camera_id, "running": False}

    def is_running(self) -> bool:
        return self._running

    def get_status(self) -> dict:
        return {
            "ok": self._running and self._cap is not None,
            "camera_id": self.camera_id,
            "running": self._running,
            "error": self._last_error,
        }


def preview_webcam(camera_id: int = 0, window_title: str = "RinoVision - Webcam Preview") -> dict:
    controller = WebcamPreviewController(camera_id=camera_id)
    start_status = controller.start()
    if not start_status.get("ok"):
        return start_status
    cv2 = controller._cv2
    try:
        while controller.is_running():
            frame = controller.read_frame()
            if frame is None:
                return {"ok": False, "error": "Could not read frame", "camera_id": camera_id}
            cv2.imshow(window_title, frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
        return {"ok": True, "camera_id": camera_id}
    finally:
        controller.stop()
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass


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
