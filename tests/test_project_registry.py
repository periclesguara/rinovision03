from pathlib import Path

from rinovision.core.artifact_registry import load_artifacts, register_artifact
from rinovision.core.project import create_project, load_project
from rinovision.paths import make_artifact_path


def test_project_and_artifact_registry_roundtrip():
    project = create_project("registry", "UPLOAD")
    loaded = load_project(project.id)
    assert loaded.id == project.id
    path = make_artifact_path("input", f"{project.id}_source.json")
    path.write_text("{}", encoding="utf-8")
    artifact = register_artifact(project, "RAW_VIDEO", path, "source")
    artifacts = load_artifacts(project.id)
    assert artifacts[0].id == artifact.id
    assert Path(artifacts[0].path).exists()
