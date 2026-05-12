from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from uuid import uuid4

from rinovision.paths import assert_inside_base, get_data_root, safe_path
from .errors import ArtifactError
from .media_types import ARTIFACT_TYPES
from .project import project_dir


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class RinoVisionArtifact:
    id: str
    project_id: str
    artifact_type: str
    path: str
    title: str = ""
    metadata: dict = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict:
        return asdict(self)


def artifacts_path(project_id: str) -> Path:
    return safe_path(project_dir(project_id), "artifacts.json")


def load_artifacts(project_id: str) -> list[RinoVisionArtifact]:
    path = artifacts_path(project_id)
    if not path.exists():
        return []
    return [RinoVisionArtifact(**item) for item in json.loads(path.read_text(encoding="utf-8"))]


def save_artifacts(project_id: str, artifacts: list[RinoVisionArtifact]) -> Path:
    path = artifacts_path(project_id)
    path.write_text(
        json.dumps([artifact.to_dict() for artifact in artifacts], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return path


def register_artifact(project, artifact_type: str, path, title: str = "", metadata=None) -> RinoVisionArtifact:
    if artifact_type not in ARTIFACT_TYPES:
        raise ArtifactError(f"invalid artifact type: {artifact_type}")
    resolved = Path(path).resolve()
    assert_inside_base(resolved, get_data_root())
    artifact = RinoVisionArtifact(
        id=str(uuid4()),
        project_id=project.id,
        artifact_type=artifact_type,
        path=str(resolved),
        title=title,
        metadata=metadata or {},
    )
    artifacts = load_artifacts(project.id)
    artifacts.append(artifact)
    save_artifacts(project.id, artifacts)
    return artifact
