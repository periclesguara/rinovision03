import json

from rinovision.core.artifact_registry import register_artifact
from rinovision.core.pipeline import transition
from rinovision.paths import make_artifact_path

from .job_models import AIVideoBrief, AIVideoPromptSet, AIVideoStoryboard, new_id


def compile_prompts(
    project,
    brief: AIVideoBrief,
    storyboard: AIVideoStoryboard,
    provider: str = "local_stub",
) -> tuple[AIVideoPromptSet, object]:
    prompts = []
    for scene in storyboard.scenes:
        prompts.append(
            {
                "scene_number": scene["scene_number"],
                "provider": provider,
                "prompt": (
                    f"{scene['visual_description']}. Camera: {scene['camera_style']}. "
                    f"Motion: {scene['motion']}. Text: {scene['on_screen_text']}."
                ),
                "negative_prompt": "no logos, no unsafe content, no distorted text, no copyrighted characters",
                "duration_seconds": scene["duration_seconds"],
                "aspect_ratio": brief.aspect_ratio,
                "language": brief.language,
                "safety_notes": "Local deterministic prompt only. Review before external provider use.",
            }
        )
    prompt_set = AIVideoPromptSet(
        id=new_id(),
        storyboard_id=storyboard.id,
        project_id=project.id,
        provider=provider,
        prompts=prompts,
    )
    path = make_artifact_path("ai_video_creator/prompts", f"{prompt_set.id}_prompts.json")
    path.write_text(json.dumps(prompt_set.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    artifact = register_artifact(project, "AI_PROMPT", path, "AI Video Creator prompt set", {"provider": provider})
    if project.status == "AI_STORYBOARD_CREATED":
        transition(project, "AI_PROMPTS_CREATED")
    return prompt_set, artifact
