from datetime import datetime, timezone
from .base import AIVideoProvider


class LocalStubVideoProvider(AIVideoProvider):
    def create_request(self, prompts: list[dict]) -> dict:
        return {
            "provider": "local_stub",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "prompts": prompts,
            "external_call": False,
        }

    def submit(self, request: dict) -> dict:
        return {
            "provider": "local_stub",
            "status": "simulated",
            "raw_video_available": False,
            "request_prompt_count": len(request.get("prompts", [])),
            "external_call": False,
        }
