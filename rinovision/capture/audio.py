class AudioCaptureAdapter:
    def __init__(self):
        self.legacy_class = get_legacy_audio_manager()
        self.available = not isinstance(self.legacy_class, dict)

    def create_legacy(self, *args, **kwargs):
        if not self.available:
            return self.legacy_class
        return self.legacy_class(*args, **kwargs)

    def status(self) -> dict:
        if self.available:
            return {"available": True, "backend": "managers.audio_manager.AudioManager"}
        return {"available": False, **self.legacy_class}


def get_legacy_audio_manager():
    try:
        from managers.audio_manager import AudioManager

        return AudioManager
    except Exception as exc:
        return {"import_error": str(exc)}
