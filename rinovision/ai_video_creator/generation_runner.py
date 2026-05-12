import json

from rinovision.core.artifact_registry import register_artifact
from rinovision.core.pipeline import transition
from rinovision.core.project import create_project
from rinovision.paths import make_artifact_path

from .brief import create_brief
from .download_manager import download_raw_video
from .import_to_editing import import_raw_video_to_editing
from .job_models import AIVideoJob
from .prompt_compiler import compile_prompts
from .provider_router import select_provider
from .script_planner import plan_script
from .social_package import create_social_package
from .storyboard_planner import plan_storyboard


def _persist_job(project, job: AIVideoJob):
    path = make_artifact_path("ai_video_creator/jobs", f"{job.id}_job.json")
    path.write_text(json.dumps(job.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    artifact = register_artifact(project, "AI_VIDEO_JOB", path, "AI Video Creator job", {"provider": job.provider, "status": job.status})
    return artifact


def run_ai_video_creator_flow(
    title: str = "RinoVision AI Video Creator Demo",
    objective: str = "Turn a creative brief into raw AI video substrate and route it into editing.",
    provider_name: str = "local_stub",
    dry_run: bool = True,
) -> dict:
    project = create_project(title, "AI_VIDEO", {"source": "ai_video_creator", "provider": provider_name})
    brief, brief_artifact = create_brief(project, title=title, objective=objective)
    script, script_artifact = plan_script(project, brief)
    storyboard, storyboard_artifact = plan_storyboard(project, script)
    prompt_set, prompt_artifact = compile_prompts(project, brief, storyboard, provider=provider_name)
    provider = select_provider(project, provider_name, dry_run=dry_run)
    prompt_payload = {
        "project_id": project.id,
        "brief_id": brief.id,
        "prompt_set_id": prompt_set.id,
        "provider": provider_name,
        "prompts": prompt_set.prompts,
    }
    job = provider.create_video_job(prompt_payload)
    if project.status == "AI_PROVIDER_SELECTED":
        transition(project, "AI_VIDEO_JOB_CREATED")
    _persist_job(project, job)
    if project.status == "AI_VIDEO_JOB_CREATED":
        transition(project, "AI_VIDEO_JOB_QUEUED")
    provider_status = provider.get_video_job(job.provider_job_id)
    if provider_status.get("status") in {"completed", "dry_run"} and project.status == "AI_VIDEO_JOB_QUEUED":
        transition(project, "AI_VIDEO_JOB_COMPLETED")
    elif project.status == "AI_VIDEO_JOB_QUEUED":
        transition(project, "AI_VIDEO_JOB_IN_PROGRESS")
    job = download_raw_video(project, provider, job)
    _persist_job(project, job)
    editing_artifact, edit_plan_artifact, import_report_path = import_raw_video_to_editing(project, job)
    social_package = create_social_package(project, brief, script)
    return {
        "project": project,
        "brief": brief,
        "script": script,
        "storyboard": storyboard,
        "prompt_set": prompt_set,
        "job": job,
        "artifacts": {
            "brief": brief_artifact,
            "script": script_artifact,
            "storyboard": storyboard_artifact,
            "prompts": prompt_artifact,
            "editing_input": editing_artifact,
            "edit_plan": edit_plan_artifact,
        },
        "import_report_path": str(import_report_path),
        "social_package_path": social_package["package_dir"],
        "social_package": social_package,
    }
