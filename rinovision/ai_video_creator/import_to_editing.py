import json

from rinovision.core.artifact_registry import register_artifact
from rinovision.core.pipeline import transition
from rinovision.editing.edit_plan import create_edit_plan
from rinovision.paths import make_artifact_path


def import_raw_video_to_editing(project, job):
    editing_input = make_artifact_path("input", f"{project.id}_{job.provider_job_id}_ai_creator_import.json")
    payload = {
        "project_id": project.id,
        "job_id": job.id,
        "provider_job_id": job.provider_job_id,
        "raw_video_path": job.raw_video_path,
        "raw_video_is_final_export": False,
        "ready_for_editing": True,
    }
    editing_input.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    raw_artifact = register_artifact(project, "RAW_AI_VIDEO", make_artifact_path("ai_video_creator/downloaded_raw", f"{job.provider_job_id}.placeholder"), "AI Creator raw video", {"final_export": False})
    source_artifact = register_artifact(project, "RAW_VIDEO", editing_input, "AI Creator raw video imported for editing", {"source": "ai_video_creator", "raw_artifact_id": raw_artifact.id})

    report_path = make_artifact_path("ai_video_creator/import_reports", f"{project.id}_{job.provider_job_id}_import_report.json")
    report = {
        "project_id": project.id,
        "job_id": job.id,
        "editing_input": str(editing_input),
        "raw_video_path": job.raw_video_path,
        "raw_video_is_final_export": False,
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    register_artifact(project, "AI_VIDEO_IMPORT_REPORT", report_path, "AI Creator import report")
    if project.status == "AI_VIDEO_DOWNLOADED":
        transition(project, "AI_VIDEO_IMPORTED_FOR_EDITING")
    edit_plan_artifact = create_edit_plan(project, source_artifact)
    return source_artifact, edit_plan_artifact, report_path
