import json

from rinovision.core.artifact_registry import register_artifact
from rinovision.core.pipeline import transition
from rinovision.paths import make_artifact_path

from .job_models import AIVideoBrief, new_id


def create_brief(
    project,
    title: str,
    objective: str,
    target_audience: str = "creators",
    platform_targets: list[str] | None = None,
    duration_seconds: int = 30,
    aspect_ratio: str = "9:16",
    language: str = "pt-BR",
    tone: str = "clear and energetic",
    call_to_action: str = "Follow RinoVision for more creator workflows.",
    source_material: dict | None = None,
) -> tuple[AIVideoBrief, object]:
    brief = AIVideoBrief(
        id=new_id(),
        project_id=project.id,
        title=title,
        objective=objective,
        target_audience=target_audience,
        platform_targets=platform_targets or ["Instagram", "Facebook", "YouTube"],
        duration_seconds=duration_seconds,
        aspect_ratio=aspect_ratio,
        language=language,
        tone=tone,
        call_to_action=call_to_action,
        source_material=source_material or {},
    )
    path = make_artifact_path("ai_video_creator/briefs", f"{brief.id}_brief.json")
    path.write_text(json.dumps(brief.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    artifact = register_artifact(project, "AI_VIDEO_BRIEF", path, "AI Video Creator brief")
    if project.status == "PROJECT_CREATED":
        transition(project, "AI_BRIEF_CREATED")
    return brief, artifact
