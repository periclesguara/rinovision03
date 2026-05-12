class TextEffectsAdapter:
    def __init__(self):
        self.legacy_module = get_legacy_text_effects_manager()
        self.available = not isinstance(self.legacy_module, dict)

    def status(self) -> dict:
        if self.available:
            return {"available": True, "backend": "managers.editor_manager.text_effects_manager"}
        return {"available": False, **self.legacy_module}


def get_legacy_text_effects_manager():
    try:
        from managers.editor_manager import text_effects_manager

        return text_effects_manager
    except Exception as exc:
        return {"import_error": str(exc)}
