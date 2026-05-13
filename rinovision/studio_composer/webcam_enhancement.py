DEFAULT_WEBCAM_ENHANCEMENT = {
    "brightness": 0,
    "contrast": 1.0,
    "saturation": 1.0,
    "gamma": 1.0,
    "mirror": True,
}


def default_webcam_enhancement() -> dict:
    return dict(DEFAULT_WEBCAM_ENHANCEMENT)


def reset_webcam_enhancement(metadata: dict) -> dict:
    metadata["enhancement"] = default_webcam_enhancement()
    return metadata["enhancement"]


def webcam_enhancement_capability() -> dict:
    missing = []
    try:
        import cv2  # noqa: F401
    except ImportError:
        missing.append("opencv-python")
    try:
        import numpy  # noqa: F401
    except ImportError:
        missing.append("numpy")
    return {
        "available": not missing,
        "missing_dependencies": missing,
        "message": "Webcam enhancement is available." if not missing else "Webcam enhancement will fall back when optional dependencies are missing.",
    }


def apply_brightness_contrast(frame, brightness=0, contrast=1.0):
    try:
        import cv2

        return cv2.convertScaleAbs(frame, alpha=float(contrast), beta=float(brightness))
    except Exception:
        return frame


def apply_saturation(frame, saturation=1.0):
    try:
        import cv2

        saturation = float(saturation)
        if saturation == 1.0:
            return frame
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
        hsv[:, :, 1] = cv2.multiply(hsv[:, :, 1], saturation)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    except Exception:
        return frame


def apply_gamma(frame, gamma=1.0):
    try:
        import cv2
        import numpy as np

        gamma = float(gamma)
        if gamma <= 0 or gamma == 1.0:
            return frame
        inverse = 1.0 / gamma
        table = np.array([(index / 255.0) ** inverse * 255 for index in range(256)]).astype("uint8")
        return cv2.LUT(frame, table)
    except Exception:
        return frame


def mirror_frame(frame):
    try:
        import cv2

        return cv2.flip(frame, 1)
    except Exception:
        try:
            return frame[:, ::-1]
        except Exception:
            return frame


def apply_webcam_enhancement(frame, settings: dict | None):
    settings = {**DEFAULT_WEBCAM_ENHANCEMENT, **(settings or {})}
    output = frame
    if settings.get("mirror", False):
        output = mirror_frame(output)
    output = apply_brightness_contrast(output, settings.get("brightness", 0), settings.get("contrast", 1.0))
    output = apply_saturation(output, settings.get("saturation", 1.0))
    output = apply_gamma(output, settings.get("gamma", 1.0))
    return output
