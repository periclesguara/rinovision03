import json

from rinovision.core.artifact_registry import register_artifact
from rinovision.core.pipeline import transition
from rinovision.paths import make_artifact_path


def generate_prompts(project, storyboard_artifact):
    storyboard = json.loads(open(storyboard_artifact.path, encoding="utf-8").read())
    artifacts = []
    for scene in storyboard.get("scenes", []):
        path = make_artifact_path("ai_video/prompts", f"{project.id}_prompt_{scene['scene']:02d}.json")
        payload = {
            "project_id": project.id,
            "storyboard_artifact_id": storyboard_artifact.id,
            "scene": scene,
            "prompt": f"Generate raw video for: {scene['description']}",
            "final_export": False,
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        artifacts.append(register_artifact(project, "AI_PROMPT", path, f"AI prompt scene {scene['scene']}", {"stub": True}))
    if project.status == "AI_STORYBOARD_CREATED":
        transition(project, "AI_PROMPTS_CREATED")
    return artifacts
