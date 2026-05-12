import json

from rinovision.core.artifact_registry import register_artifact
from rinovision.core.pipeline import transition
from rinovision.paths import make_artifact_path


def generate_script(project, brief: str):
    path = make_artifact_path("ai_video/scripts", f"{project.id}_script.json")
    payload = {
        "project_id": project.id,
        "brief": brief,
        "script": f"Stub script generated from brief: {brief}",
        "status": "stub",
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    artifact = register_artifact(project, "AI_SCRIPT", path, "AI video script", {"stub": True})
    if project.status == "PROJECT_CREATED":
        transition(project, "AI_SCRIPT_CREATED")
    return artifact
