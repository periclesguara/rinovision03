import json
from pathlib import Path

from rinovision.ai_video.providers.local_stub import LocalStubVideoProvider
from rinovision.core.artifact_registry import register_artifact
from rinovision.core.pipeline import transition
from rinovision.paths import make_artifact_path


def create_provider_request(project, prompts):
    provider = LocalStubVideoProvider()
    prompt_payloads = [json.loads(Path(artifact.path).read_text(encoding="utf-8")) for artifact in prompts]
    request = provider.create_request(prompt_payloads)
    path = make_artifact_path("ai_video/provider_requests", f"{project.id}_provider_request.json")
    path.write_text(json.dumps(request, indent=2, ensure_ascii=False), encoding="utf-8")
    artifact = register_artifact(project, "AI_PROVIDER_REQUEST", path, "AI provider request", {"provider": "local_stub"})
    if project.status == "AI_PROMPTS_CREATED":
        transition(project, "AI_VIDEO_REQUESTED")
    return artifact


def simulate_provider_response(project, request_artifact):
    provider = LocalStubVideoProvider()
    request = json.loads(Path(request_artifact.path).read_text(encoding="utf-8"))
    response = provider.submit(request)
    path = make_artifact_path("ai_video/provider_responses", f"{project.id}_provider_response.json")
    path.write_text(json.dumps(response, indent=2, ensure_ascii=False), encoding="utf-8")
    return register_artifact(project, "AI_PROVIDER_RESPONSE", path, "AI provider response", {"provider": "local_stub"})


def import_raw_ai_video(project, source_path=None):
    path = make_artifact_path("ai_video/generated_raw", f"{project.id}_raw_ai_video_placeholder.json")
    placeholder_path = make_artifact_path("ai_video/generated_raw", f"{project.id}_raw_ai_video.placeholder")
    payload = {
        "project_id": project.id,
        "source_path": str(source_path) if source_path else None,
        "placeholder_path": str(placeholder_path),
        "artifact_kind": "raw_ai_video_placeholder",
        "final_export": False,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    placeholder_path.write_text("RinoVision raw AI video placeholder. Not a final export.\n", encoding="utf-8")
    artifact = register_artifact(project, "RAW_AI_VIDEO", path, "Raw AI video placeholder", {"final_export": False})
    if project.status == "AI_VIDEO_REQUESTED":
        transition(project, "AI_VIDEO_GENERATED_RAW")
    return artifact


def send_to_editing(project, raw_video_artifact):
    path = make_artifact_path("input", f"{project.id}_ai_video_import.json")
    payload = {
        "project_id": project.id,
        "source_artifact_id": raw_video_artifact.id,
        "source_path": raw_video_artifact.path,
        "ready_for_editing": True,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    artifact = register_artifact(project, "RAW_VIDEO", path, "AI raw video imported for editing", {"source": "ai_video"})
    if project.status == "AI_VIDEO_GENERATED_RAW":
        transition(project, "AI_VIDEO_IMPORTED_FOR_EDITING")
    return artifact
