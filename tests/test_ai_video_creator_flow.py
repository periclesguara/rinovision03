import json
from pathlib import Path

import pytest

from rinovision.ai_video_creator import run_ai_video_creator_flow
from rinovision.paths import make_artifact_path


def test_ai_video_creator_package_imports_safely():
    import rinovision.ai_video_creator as creator

    assert callable(creator.run_ai_video_creator_flow)


def test_local_creator_flow_creates_assets_and_routes_to_editing():
    result = run_ai_video_creator_flow(title="Creator Flow Test", objective="Validate local stub flow.")
    project = result["project"]
    job = result["job"]

    assert result["brief"].id
    assert result["script"].scenes
    assert result["storyboard"].scenes
    assert result["prompt_set"].prompts
    assert Path(job.raw_video_path).exists()
    assert job.status == "downloaded"
    assert project.status == "AI_SOCIAL_PACKAGE_CREATED"
    assert result["artifacts"]["editing_input"].artifact_type == "RAW_VIDEO"
    assert result["artifacts"]["edit_plan"].artifact_type == "EDIT_PLAN"
    assert Path(result["social_package_path"]).exists()
    assert Path(result["social_package"]["files"]["instagram_caption.txt"]).exists()
    assert Path(result["social_package"]["files"]["facebook_caption.txt"]).exists()
    assert Path(result["social_package"]["files"]["youtube_title.txt"]).exists()


def test_raw_ai_video_is_not_export_ready():
    result = run_ai_video_creator_flow(title="Raw Is Substrate", objective="Keep raw video out of exports.")
    raw_path = Path(result["job"].raw_video_path)
    assert raw_path.suffix == ".placeholder"
    assert "Not a final export" in raw_path.read_text(encoding="utf-8")
    assert result["project"].status != "EXPORT_READY"


def test_ai_video_creator_path_traversal_rejected():
    with pytest.raises(Exception):
        make_artifact_path("ai_video_creator/briefs", "../escape.json")


def test_healthcheck_reports_ai_video_creator():
    from scripts.rinovision_healthcheck import run_healthcheck

    report = run_healthcheck()
    assert report["ai_video_creator"]["package_import"]["ok"] is True
    assert report["ai_video_creator"]["local_stub_provider_import"]["ok"] is True
