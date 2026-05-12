from rinovision.ai_video.prompt_builder import generate_prompts
from rinovision.ai_video.raw_video_importer import (
    create_provider_request,
    import_raw_ai_video,
    send_to_editing,
    simulate_provider_response,
)
from rinovision.ai_video.script_generator import generate_script
from rinovision.ai_video.storyboard import generate_storyboard
from rinovision.core.project import create_project


def test_ai_video_stub_flow_routes_raw_video_to_editing():
    project = create_project("ai flow", "AI_VIDEO")
    script = generate_script(project, "short product launch")
    storyboard = generate_storyboard(project, script)
    prompts = generate_prompts(project, storyboard)
    request = create_provider_request(project, prompts)
    response = simulate_provider_response(project, request)
    raw = import_raw_ai_video(project)
    imported = send_to_editing(project, raw)

    assert project.status == "AI_VIDEO_IMPORTED_FOR_EDITING"
    assert script.artifact_type == "AI_SCRIPT"
    assert storyboard.artifact_type == "AI_STORYBOARD"
    assert prompts
    assert response.artifact_type == "AI_PROVIDER_RESPONSE"
    assert raw.artifact_type == "RAW_AI_VIDEO"
    assert raw.metadata["final_export"] is False
    assert imported.artifact_type == "RAW_VIDEO"
