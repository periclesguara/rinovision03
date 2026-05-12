def _load_webcam_dependencies():
    try:
        import cv2
        import mediapipe as mp
        import numpy as np
    except ImportError as exc:
        raise RuntimeError(f"[webcam_manager_refactorv1] Missing webcam dependency: {exc.name}") from exc
    return cv2, np, mp

class WebcamManager:
    def __init__(self):
        self.cv2, self.np, self.mp = _load_webcam_dependencies()
        cv2 = self.cv2
        mp = self.mp
        self.cap = cv2.VideoCapture(0)
        self.blur = False
        self.bg_color = (0, 0, 0)
        self.effect = None

        self.mp_selfie = mp.solutions.selfie_segmentation
        self.segmentor = self.mp_selfie.SelfieSegmentation(model_selection=1)

    def read_frame(self):
        cv2 = self.cv2
        np = self.np
        ret, frame = self.cap.read()
        if not ret:
            return None

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.segmentor.process(rgb)

        if results.segmentation_mask is not None:
            mask = results.segmentation_mask > 0.5
            bg_image = self.get_background(frame)
            frame = np.where(mask[..., None], frame, bg_image)

        return frame

    def get_background(self, frame):
        cv2 = self.cv2
        np = self.np
        if self.effect == "blur":
            return cv2.GaussianBlur(frame, (55, 55), 0)
        elif self.effect == "white":
            return np.ones_like(frame) * 255
        elif self.effect == "black":
            return np.zeros_like(frame)
        elif self.effect == "transparent":
            # Transparente no OpenCV não existe. Retorna o frame sem fundo (alpha fake)
            h, w, _ = frame.shape
            transparent = np.zeros((h, w, 4), dtype=np.uint8)
            mask = self.segmentor.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).segmentation_mask > 0.5
            transparent[..., :3] = frame
            transparent[..., 3] = (mask * 255).astype(np.uint8)
            return transparent
        else:
            return frame

    def set_effect(self, effect_name):
        self.effect = effect_name

    def release(self):
        self.cap.release()
