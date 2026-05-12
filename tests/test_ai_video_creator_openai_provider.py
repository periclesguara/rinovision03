import json
from pathlib import Path

from rinovision.ai_video_creator.providers.openai_video import OpenAIVideoProvider


def test_openai_video_adapter_imports_without_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    provider = OpenAIVideoProvider()
    capability = provider.capability()
    assert capability["dry_run"] is True
    assert capability["api_key_present"] is False


def test_openai_video_adapter_dry_run_does_not_call_network(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "OPENAI_API_KEY_TEST_VALUE")
    provider = OpenAIVideoProvider(dry_run=True)
    payload = {"project_id": "test-project", "prompts": [{"prompt": "local dry run"}]}
    job = provider.create_video_job(payload)

    assert job.provider == "openai_video"
    assert job.status == "dry_run"
    assert Path(job.request_path).exists()
    assert Path(job.response_path).exists()
    combined = Path(job.request_path).read_text(encoding="utf-8") + Path(job.response_path).read_text(encoding="utf-8")
    assert "OPENAI_API_KEY_TEST_VALUE" not in combined
    assert "OPENAI_API_KEY" not in combined


def test_openai_video_missing_key_runtime_error_status(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    provider = OpenAIVideoProvider(dry_run=False)
    job = provider.create_video_job({"project_id": "test-project", "prompts": []})
    response = json.loads(Path(job.response_path).read_text(encoding="utf-8"))
    assert job.status == "error"
    assert response["error_message"] == "API key is not configured."
    assert "OPENAI_API_KEY" not in Path(job.response_path).read_text(encoding="utf-8")
