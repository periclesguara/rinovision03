import json
from pathlib import Path

from rinovision.core.artifact_registry import register_artifact
from rinovision.core.pipeline import transition
from rinovision.paths import make_artifact_path


def render_basic_edit(project, edit_plan_artifact):
    plan = json.loads(Path(edit_plan_artifact.path).read_text(encoding="utf-8"))
    path = make_artifact_path("edited_videos", f"{project.id}_edited_video.placeholder")
    payload = {
        "project_id": project.id,
        "edit_plan_artifact_id": edit_plan_artifact.id,
        "source_path": plan.get("source_path"),
        "artifact_kind": "edited_video_placeholder",
        "final_export": False,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    artifact = register_artifact(project, "EDITED_VIDEO", path, "Edited video placeholder", {"stub": True})
    if project.status == "EDIT_PLAN_CREATED":
        transition(project, "VIDEO_EDITED")
    return artifact
