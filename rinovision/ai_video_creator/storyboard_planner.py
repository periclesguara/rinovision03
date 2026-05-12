import json

from rinovision.core.artifact_registry import register_artifact
from rinovision.core.pipeline import transition
from rinovision.paths import make_artifact_path

from .job_models import AIVideoScript, AIVideoStoryboard, new_id


def plan_storyboard(project, script: AIVideoScript) -> tuple[AIVideoStoryboard, object]:
    scenes = []
    for index, scene in enumerate(script.scenes):
        scenes.append(
            {
                "scene_number": scene["scene_number"],
                "visual_description": f"Clean creator-tech visual for {scene['summary']}",
                "camera_style": "stable close-up with UI overlay",
                "motion": "subtle push-in and animated text reveal",
                "duration_seconds": scene["duration_seconds"],
                "narration": script.narration[index],
                "on_screen_text": script.on_screen_text[index],
            }
        )
    storyboard = AIVideoStoryboard(id=new_id(), script_id=script.id, project_id=project.id, scenes=scenes)
    path = make_artifact_path("ai_video_creator/storyboards", f"{storyboard.id}_storyboard.json")
    path.write_text(json.dumps(storyboard.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    artifact = register_artifact(project, "AI_STORYBOARD", path, "AI Video Creator storyboard")
    if project.status == "AI_SCRIPT_CREATED":
        transition(project, "AI_STORYBOARD_CREATED")
    return storyboard, artifact
