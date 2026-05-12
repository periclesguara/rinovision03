import json
import os

from rinovision.ai_video_creator.job_models import AIVideoJob, new_id, utc_now
from rinovision.paths import make_artifact_path

from .base import AIVideoProvider


class OpenAIVideoProvider(AIVideoProvider):
    name = "openai_video"

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run

    def capability(self) -> dict:
        return {
            "provider": self.name,
            "dry_run": self.dry_run,
            "api_key_present": bool(os.getenv("OPENAI_API_KEY")),
            "external_calls_enabled": not self.dry_run and bool(os.getenv("OPENAI_API_KEY")),
        }

    def create_video_job(self, prompt_payload: dict) -> AIVideoJob:
        project_id = prompt_payload["project_id"]
        provider_job_id = f"openai-dry-run-{new_id()}"
        sanitized_payload = dict(prompt_payload)
        sanitized_payload["provider"] = self.name
        sanitized_payload["dry_run"] = self.dry_run
        request_path = make_artifact_path("ai_video_creator/provider_requests", f"{provider_job_id}_request.json")
        response_path = make_artifact_path("ai_video_creator/provider_responses", f"{provider_job_id}_response.json")
        request_path.write_text(json.dumps(sanitized_payload, indent=2, ensure_ascii=False), encoding="utf-8")
        response = {
            "provider": self.name,
            "provider_job_id": provider_job_id,
            "status": "dry_run" if self.dry_run else "not_implemented",
            "capability": self.capability(),
            "message": "OpenAI video provider dry-run. No network call was made.",
            "created_at": utc_now(),
        }
        if not self.dry_run and not os.getenv("OPENAI_API_KEY"):
            response["status"] = "error"
            response["error_message"] = "API key is not configured."
        response_path.write_text(json.dumps(response, indent=2, ensure_ascii=False), encoding="utf-8")
        return AIVideoJob(
            id=new_id(),
            project_id=project_id,
            provider=self.name,
            provider_job_id=provider_job_id,
            status=response["status"],
            request_path=str(request_path),
            response_path=str(response_path),
            error_message=response.get("error_message", ""),
        )

    def get_video_job(self, job_id: str) -> dict:
        return {
            "provider": self.name,
            "provider_job_id": job_id,
            "status": "dry_run",
            "message": "Dry-run provider does not poll network jobs.",
        }

    def download_video(self, job_id: str, destination_path: str) -> dict:
        if not self.dry_run and not os.getenv("OPENAI_API_KEY"):
            return {"provider": self.name, "provider_job_id": job_id, "status": "error", "error_message": "API key is not configured."}
        with open(destination_path, "w", encoding="utf-8") as handle:
            handle.write("OpenAI video dry-run placeholder. Not a final export.\n")
        return {"provider": self.name, "provider_job_id": job_id, "status": "downloaded", "raw_video_path": destination_path}
