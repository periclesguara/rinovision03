import json

from rinovision.ai_video_creator.job_models import AIVideoJob, new_id, utc_now
from rinovision.paths import make_artifact_path

from .base import AIVideoProvider


class LocalStubVideoProvider(AIVideoProvider):
    name = "local_stub"

    def create_video_job(self, prompt_payload: dict) -> AIVideoJob:
        project_id = prompt_payload["project_id"]
        provider_job_id = f"local-{new_id()}"
        request_path = make_artifact_path("ai_video_creator/provider_requests", f"{provider_job_id}_request.json")
        response_path = make_artifact_path("ai_video_creator/provider_responses", f"{provider_job_id}_response.json")
        request_path.write_text(json.dumps(prompt_payload, indent=2, ensure_ascii=False), encoding="utf-8")
        response = {
            "provider": self.name,
            "provider_job_id": provider_job_id,
            "status": "completed",
            "external_call": False,
            "created_at": utc_now(),
        }
        response_path.write_text(json.dumps(response, indent=2, ensure_ascii=False), encoding="utf-8")
        return AIVideoJob(
            id=new_id(),
            project_id=project_id,
            provider=self.name,
            provider_job_id=provider_job_id,
            status="completed",
            request_path=str(request_path),
            response_path=str(response_path),
        )

    def get_video_job(self, job_id: str) -> dict:
        return {"provider": self.name, "provider_job_id": job_id, "status": "completed", "external_call": False}

    def download_video(self, job_id: str, destination_path: str) -> dict:
        with open(destination_path, "w", encoding="utf-8") as handle:
            handle.write("RinoVision AI Video Creator raw video placeholder. Not a final export.\n")
        return {
            "provider": self.name,
            "provider_job_id": job_id,
            "status": "downloaded",
            "raw_video_path": destination_path,
            "external_call": False,
        }
