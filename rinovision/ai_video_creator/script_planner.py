import json

from rinovision.core.artifact_registry import register_artifact
from rinovision.core.pipeline import transition
from rinovision.paths import make_artifact_path

from .job_models import AIVideoBrief, AIVideoScript, new_id


def plan_script(project, brief: AIVideoBrief) -> tuple[AIVideoScript, object]:
    scene_duration = max(1, brief.duration_seconds // 3)
    scenes = [
        {
            "scene_number": 1,
            "purpose": "hook",
            "duration_seconds": scene_duration,
            "summary": f"Introduce {brief.title} for {brief.target_audience}.",
        },
        {
            "scene_number": 2,
            "purpose": "value",
            "duration_seconds": scene_duration,
            "summary": brief.objective,
        },
        {
            "scene_number": 3,
            "purpose": "call_to_action",
            "duration_seconds": brief.duration_seconds - (scene_duration * 2),
            "summary": brief.call_to_action,
        },
    ]
    narration = [
        f"Here is {brief.title}, built for {brief.target_audience}.",
        f"The goal is simple: {brief.objective}.",
        brief.call_to_action,
    ]
    on_screen_text = [brief.title, brief.objective[:80], brief.call_to_action[:80]]
    script = AIVideoScript(
        id=new_id(),
        brief_id=brief.id,
        project_id=project.id,
        scenes=scenes,
        narration=narration,
        on_screen_text=on_screen_text,
    )
    path = make_artifact_path("ai_video_creator/scripts", f"{script.id}_script.json")
    path.write_text(json.dumps(script.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    artifact = register_artifact(project, "AI_SCRIPT", path, "AI Video Creator script")
    if project.status == "AI_BRIEF_CREATED":
        transition(project, "AI_SCRIPT_CREATED")
    return script, artifact
