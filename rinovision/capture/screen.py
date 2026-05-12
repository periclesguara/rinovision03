class ScreenCaptureAdapter:
    def __init__(self):
        self.legacy_class = get_legacy_record_manager()
        self.available = not isinstance(self.legacy_class, dict)

    def create_legacy(self, *args, **kwargs):
        if not self.available:
            return self.legacy_class
        return self.legacy_class(*args, **kwargs)

    def status(self) -> dict:
        if self.available:
            return {"available": True, "backend": "managers.record_manager.RecordManager"}
        return {"available": False, **self.legacy_class}


def get_legacy_record_manager():
    try:
        from managers.record_manager import RecordManager

        return RecordManager
    except Exception as exc:
        return {"import_error": str(exc)}
