from pathlib import Path


def _import_cv2():
    try:
        import cv2
    except ImportError:
        return None
    return cv2


class VideoLayerPlayer:
    def __init__(self, video_path: str | Path):
        self.video_path = str(video_path)
        self._cv2 = None
        self._cap = None
        self._playing = False
        self._last_error = ""

    def play(self) -> dict:
        if self._playing and self._cap is not None:
            return self.status()
        cv2 = _import_cv2()
        if cv2 is None:
            self._last_error = "OpenCV is required for video playback preview."
            return {"ok": False, "error": self._last_error, "missing_dependencies": ["opencv-python"]}
        if not Path(self.video_path).exists():
            self._last_error = "Video file not found."
            return {"ok": False, "error": self._last_error}
        self._cv2 = cv2
        self._cap = cv2.VideoCapture(self.video_path)
        if not self._cap or not self._cap.isOpened():
            self._last_error = "Could not open video preview."
            self.pause()
            return {"ok": False, "error": self._last_error}
        self._playing = True
        self._last_error = ""
        return self.status()

    def read_frame(self):
        if not self._playing or self._cap is None:
            return None
        ok, frame = self._cap.read()
        if not ok:
            self.pause()
            return None
        return frame

    def pause(self) -> dict:
        cap = self._cap
        self._cap = None
        self._playing = False
        if cap is not None:
            cap.release()
        return self.status()

    def is_playing(self) -> bool:
        return self._playing

    def status(self) -> dict:
        return {"ok": self._playing, "playing": self._playing, "path": self.video_path, "error": self._last_error}
