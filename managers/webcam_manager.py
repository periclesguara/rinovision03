def _load_webcam_dependencies():
    try:
        import cv2
        import mediapipe as mp
        import numpy as np
    except ImportError as exc:
        raise RuntimeError(f"[webcam_manager] Missing webcam dependency: {exc.name}") from exc
    return cv2, np, mp


class WebcamManager:
    def __init__(self):
        self.cv2, self.np, self.mp = _load_webcam_dependencies()
        cv2 = self.cv2
        mp = self.mp
        self.cap = cv2.VideoCapture(0)
        self.effect_mode = "transparent"
        self.segmentation = mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=1)

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return self.apply_effect(frame)

    def apply_effect(self, frame):
        cv2 = self.cv2
        np = self.np
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.segmentation.process(rgb_frame)
        mask = (result.segmentation_mask > 0.5).astype(np.uint8)

        if self.effect_mode == "transparent":
            return self._apply_transparency(frame, mask)
        elif self.effect_mode == "blur":
            return self._apply_blur(frame, mask)
        elif self.effect_mode == "black":
            return self._apply_background_color(frame, mask, (0, 0, 0))
        elif self.effect_mode == "white":
            return self._apply_background_color(frame, mask, (255, 255, 255))
        else:
            return frame

    def _apply_transparency(self, frame, mask):
        cv2 = self.cv2
        fg = cv2.bitwise_and(frame, frame, mask=mask)
        bgra = cv2.cvtColor(fg, cv2.COLOR_BGR2BGRA)
        bgra[..., 3] = mask * 255
        return bgra

    def _apply_blur(self, frame, mask):
        cv2 = self.cv2
        blurred = cv2.GaussianBlur(frame, (55, 55), 0)
        fg = cv2.bitwise_and(frame, frame, mask=mask)
        bg = cv2.bitwise_and(blurred, blurred, mask=1 - mask)
        return cv2.add(fg, bg)

    def _apply_background_color(self, frame, mask, color=(0, 0, 0)):
        cv2 = self.cv2
        np = self.np
        bg = np.full_like(frame, color, dtype=np.uint8)
        fg = cv2.bitwise_and(frame, frame, mask=mask)
        bg = cv2.bitwise_and(bg, bg, mask=1 - mask)
        return cv2.add(fg, bg)

    def set_effect(self, mode: str):
        self.effect_mode = mode

    def release(self):
        if self.cap:
            self.cap.release()
