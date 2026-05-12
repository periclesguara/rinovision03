from rinovision.core.artifact_registry import register_artifact
from rinovision.paths import make_artifact_path


class SubtitleAdapter:
    def __init__(self):
        self.legacy_module = get_legacy_subtitle_manager()
        self.available = not isinstance(self.legacy_module, dict)

    def status(self) -> dict:
        if self.available:
            return {"available": True, "backend": "managers.editor_manager.subtitle_manager"}
        return {"available": False, **self.legacy_module}


def generate_subtitles_placeholder(project, text=None):
    path = make_artifact_path("subtitles", f"{project.id}_subtitles.srt")
    content = "1\n00:00:00,000 --> 00:00:03,000\n" + (text or "Legenda placeholder RinoVision") + "\n"
    path.write_text(content, encoding="utf-8")
    return register_artifact(project, "SUBTITLE", path, "Subtitle placeholder", {"stub": True})


def get_legacy_subtitle_manager():
    try:
        from managers.editor_manager import subtitle_manager

        return subtitle_manager
    except Exception as exc:
        return {"import_error": str(exc)}
