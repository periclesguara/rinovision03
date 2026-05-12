import os
from pathlib import Path

from rinovision.core.errors import ArtifactError, PathSafetyError


CATEGORIES = {
    "input": "input",
    "output": "output",
    "tmp": "tmp",
    "audio": "audio",
    "video": "video",
    "images": "images",
    "frames": "frames",
    "subtitles": "subtitles",
    "exports": "exports",
    "reports": "reports",
    "projects": "projects",
    "ai_video/scripts": "ai_video/scripts",
    "ai_video/storyboards": "ai_video/storyboards",
    "ai_video/prompts": "ai_video/prompts",
    "ai_video/generated_raw": "ai_video/generated_raw",
    "ai_video/provider_requests": "ai_video/provider_requests",
    "ai_video/provider_responses": "ai_video/provider_responses",
    "ai_video_creator/briefs": "ai_video_creator/briefs",
    "ai_video_creator/scripts": "ai_video_creator/scripts",
    "ai_video_creator/storyboards": "ai_video_creator/storyboards",
    "ai_video_creator/prompts": "ai_video_creator/prompts",
    "ai_video_creator/jobs": "ai_video_creator/jobs",
    "ai_video_creator/provider_requests": "ai_video_creator/provider_requests",
    "ai_video_creator/provider_responses": "ai_video_creator/provider_responses",
    "ai_video_creator/downloaded_raw": "ai_video_creator/downloaded_raw",
    "ai_video_creator/import_reports": "ai_video_creator/import_reports",
    "ai_video_creator/social_packages": "ai_video_creator/social_packages",
    "ai_video_creator/reports": "ai_video_creator/reports",
    "edited_videos": "edited_videos",
    "edit_plans": "edit_plans",
}


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def get_data_root() -> Path:
    configured = os.getenv("RINOVISION_DATA_ROOT")
    root = Path(configured) if configured else get_project_root() / "data"
    if not root.is_absolute():
        root = get_project_root() / root
    return root.resolve()


def assert_inside_base(path, base) -> Path:
    resolved_path = Path(path).resolve()
    resolved_base = Path(base).resolve()
    try:
        resolved_path.relative_to(resolved_base)
    except ValueError as exc:
        raise PathSafetyError(f"path escapes base: {resolved_path}") from exc
    return resolved_path


def safe_path(base, *parts) -> Path:
    base_path = Path(base).resolve()
    candidate = base_path.joinpath(*parts)
    return assert_inside_base(candidate, base_path)


def ensure_data_dirs() -> Path:
    root = get_data_root()
    root.mkdir(parents=True, exist_ok=True)
    for relative in CATEGORIES.values():
        safe_path(root, relative).mkdir(parents=True, exist_ok=True)
    return root


def make_artifact_path(category: str, filename: str) -> Path:
    if category not in CATEGORIES:
        raise ArtifactError(f"unknown artifact category: {category}")
    if Path(filename).name != filename:
        raise PathSafetyError("artifact filename must not contain directories")
    data_root = ensure_data_dirs()
    target_dir = safe_path(data_root, CATEGORIES[category])
    return safe_path(target_dir, filename)
