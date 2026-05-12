from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from uuid import uuid4

from rinovision.paths import ensure_data_dirs, safe_path
from .errors import ProjectError
from .media_types import PROJECT_TYPES


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class RinoVisionProject:
    id: str
    name: str
    project_type: str
    status: str = "PROJECT_CREATED"
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    metadata: dict = field(default_factory=dict)

    def touch(self) -> None:
        self.updated_at = utc_now()

    def to_dict(self) -> dict:
        return asdict(self)


def create_project(name: str, project_type: str, metadata=None) -> RinoVisionProject:
    if project_type not in PROJECT_TYPES:
        raise ProjectError(f"invalid project type: {project_type}")
    project = RinoVisionProject(
        id=str(uuid4()),
        name=name,
        project_type=project_type,
        metadata=metadata or {},
    )
    save_project(project)
    return project


def project_dir(project_id: str) -> Path:
    root = ensure_data_dirs()
    path = safe_path(root, "projects", project_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


def project_manifest_path(project_id: str) -> Path:
    return safe_path(project_dir(project_id), "project.json")


def save_project(project: RinoVisionProject) -> Path:
    path = project_manifest_path(project.id)
    path.write_text(json.dumps(project.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def load_project(project_id: str) -> RinoVisionProject:
    data = json.loads(project_manifest_path(project_id).read_text(encoding="utf-8"))
    return RinoVisionProject(**data)
