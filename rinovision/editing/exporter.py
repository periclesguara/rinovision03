import json

from rinovision.core.artifact_registry import register_artifact
from rinovision.core.pipeline import transition
from rinovision.paths import make_artifact_path


class ExportAdapter:
    def __init__(self):
        self.legacy_module = get_legacy_export_manager()
        self.available = not isinstance(self.legacy_module, dict)

    def status(self) -> dict:
        if self.available:
            return {"available": True, "backend": "managers.editor_manager.export_manager"}
        return {"available": False, **self.legacy_module}


def generate_thumbnail_placeholder(project):
    path = make_artifact_path("images", f"{project.id}_thumbnail_placeholder.json")
    path.write_text(json.dumps({"project_id": project.id, "thumbnail": "placeholder"}, indent=2), encoding="utf-8")
    return register_artifact(project, "THUMBNAIL", path, "Thumbnail placeholder", {"stub": True})


def export_package(project, artifacts):
    artifact_refs = [
        {"id": artifact.id, "type": artifact.artifact_type, "path": artifact.path}
        for artifact in artifacts
        if artifact.artifact_type != "RAW_AI_VIDEO"
    ]
    path = make_artifact_path("exports", f"{project.id}_export_package.json")
    payload = {"project_id": project.id, "artifacts": artifact_refs, "contains_raw_ai_video_as_final": False}
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    artifact = register_artifact(project, "EXPORT_PACKAGE", path, "Export package", {"stub": True})
    if project.status in {"VIDEO_EDITED", "THUMBNAIL_GENERATED", "QC_APPROVED"}:
        transition(project, "EXPORT_READY")
    return artifact


def get_legacy_export_manager():
    try:
        from managers.editor_manager import export_manager

        return export_manager
    except Exception as exc:
        return {"import_error": str(exc)}
