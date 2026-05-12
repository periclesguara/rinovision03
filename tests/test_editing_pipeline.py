from rinovision.core.project import create_project
from rinovision.core.artifact_registry import register_artifact
from rinovision.editing.compositor import render_basic_edit
from rinovision.editing.edit_plan import create_edit_plan
from rinovision.editing.exporter import export_package
from rinovision.editing.video_probe import probe_video
from rinovision.paths import make_artifact_path


def test_editing_pipeline_creates_plan_and_export_package():
    project = create_project("editing", "UPLOAD")
    source_path = make_artifact_path("input", f"{project.id}_video_placeholder.json")
    source_path.write_text("{}", encoding="utf-8")
    source = register_artifact(project, "RAW_VIDEO", source_path, "source")
    plan = create_edit_plan(project, source)
    edited = render_basic_edit(project, plan)
    package = export_package(project, [edited])
    assert plan.artifact_type == "EDIT_PLAN"
    assert edited.artifact_type == "EDITED_VIDEO"
    assert package.artifact_type == "EXPORT_PACKAGE"


def test_missing_ffmpeg_does_not_crash_probe(monkeypatch):
    monkeypatch.setattr("rinovision.editing.video_probe.command_available", lambda command: False)
    result = probe_video("/tmp/missing.mp4")
    assert result["ok"] is False
    assert result["dependency_missing"] == "ffprobe"
