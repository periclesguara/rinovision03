import json

from rinovision.core.artifact_registry import register_artifact
from rinovision.core.pipeline import transition
from rinovision.paths import ensure_data_dirs, safe_path


def create_social_package(project, brief, script) -> dict:
    package_dir = safe_path(ensure_data_dirs(), "ai_video_creator", "social_packages", f"{project.id}_social_package")
    package_dir.mkdir(parents=True, exist_ok=True)
    hashtags = ["#RinoVision", "#AIVideo", "#CreatorWorkflow", "#VideoEditing"]
    files = {
        "instagram_caption.txt": f"{brief.title}\n\n{brief.call_to_action}\n{' '.join(hashtags)}\n",
        "facebook_caption.txt": f"{brief.title}\n\n{brief.objective}\n\n{brief.call_to_action}\n",
        "youtube_title.txt": brief.title[:90] + "\n",
        "youtube_description.txt": "\n".join(script.narration) + f"\n\n{brief.call_to_action}\n",
        "hashtags.txt": "\n".join(hashtags) + "\n",
    }
    written = {}
    for filename, content in files.items():
        path = safe_path(package_dir, filename)
        path.write_text(content, encoding="utf-8")
        written[filename] = str(path)
    metadata_path = safe_path(package_dir, "package_metadata.json")
    metadata = {
        "project_id": project.id,
        "brief_id": brief.id,
        "platforms": ["Instagram", "Facebook", "YouTube"],
        "auto_publish": False,
        "manual_upload_required": True,
        "files": written,
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    written["package_metadata.json"] = str(metadata_path)
    register_artifact(project, "AI_VIDEO_SOCIAL_PACKAGE", metadata_path, "AI Creator social package", {"auto_publish": False})
    if project.status == "EDIT_PLAN_CREATED":
        transition(project, "AI_SOCIAL_PACKAGE_CREATED")
    return {"package_dir": str(package_dir), "files": written}
