import json

from rinovision.ai_video_creator.job_models import AIVideoJob
from rinovision.core.pipeline import transition
from rinovision.paths import make_artifact_path


def download_raw_video(project, provider, job: AIVideoJob) -> AIVideoJob:
    destination = make_artifact_path("ai_video_creator/downloaded_raw", f"{job.provider_job_id}.placeholder")
    result = provider.download_video(job.provider_job_id, str(destination))
    report_path = make_artifact_path("ai_video_creator/reports", f"{job.provider_job_id}_download_report.json")
    report_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    job.raw_video_path = str(destination)
    job.touch("downloaded")
    if project.status == "AI_VIDEO_JOB_COMPLETED":
        transition(project, "AI_VIDEO_DOWNLOADED")
    return job
