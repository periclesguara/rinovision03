import json

from rinovision.core.artifact_registry import register_artifact
from rinovision.core.pipeline import transition
from rinovision.paths import make_artifact_path


def generate_storyboard(project, script_artifact):
    path = make_artifact_path("ai_video/storyboards", f"{project.id}_storyboard.json")
    payload = {
        "project_id": project.id,
        "script_artifact_id": script_artifact.id,
        "scenes": [
            {"scene": 1, "description": "Opening hook", "duration_seconds": 3},
            {"scene": 2, "description": "Main visual explanation", "duration_seconds": 8},
            {"scene": 3, "description": "Closing call to action", "duration_seconds": 3},
        ],
        "status": "stub",
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    artifact = register_artifact(project, "AI_STORYBOARD", path, "AI video storyboard", {"stub": True})
    if project.status == "AI_SCRIPT_CREATED":
        transition(project, "AI_STORYBOARD_CREATED")
    return artifact
