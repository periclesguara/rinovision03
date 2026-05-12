import json
from pathlib import Path

from rinovision.core.artifact_registry import register_artifact
from rinovision.core.pipeline import transition
from rinovision.paths import make_artifact_path
from .video_probe import probe_video


def create_edit_plan(project, source_video_artifact, options=None):
    report = probe_video(source_video_artifact.path)
    report_path = make_artifact_path("reports", f"{project.id}_video_probe_report.json")
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    register_artifact(project, "REPORT", report_path, "Video probe report", {"source": source_video_artifact.id})

    path = make_artifact_path("edit_plans", f"{project.id}_edit_plan.json")
    plan = {
        "project_id": project.id,
        "source_artifact_id": source_video_artifact.id,
        "source_path": source_video_artifact.path,
        "options": options or {},
        "steps": ["normalize_source", "compose_tracks", "prepare_export"],
        "raw_ai_video_is_final": False,
    }
    path.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
    artifact = register_artifact(project, "EDIT_PLAN", path, "Edit plan", {"stub": True})
    if project.status in {"PROJECT_CREATED", "MEDIA_IMPORTED", "AI_VIDEO_IMPORTED_FOR_EDITING"}:
        transition(project, "EDIT_PLAN_CREATED")
    return artifact
