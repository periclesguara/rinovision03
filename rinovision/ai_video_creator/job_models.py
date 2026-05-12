from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id() -> str:
    return str(uuid4())


@dataclass
class AIVideoBrief:
    id: str
    project_id: str
    title: str
    objective: str
    target_audience: str
    platform_targets: list[str]
    duration_seconds: int
    aspect_ratio: str
    language: str
    tone: str
    call_to_action: str
    source_material: dict
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AIVideoScript:
    id: str
    brief_id: str
    project_id: str
    scenes: list[dict]
    narration: list[str]
    on_screen_text: list[str]
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AIVideoStoryboard:
    id: str
    script_id: str
    project_id: str
    scenes: list[dict]
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AIVideoPromptSet:
    id: str
    storyboard_id: str
    project_id: str
    provider: str
    prompts: list[dict]
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AIVideoJob:
    id: str
    project_id: str
    provider: str
    provider_job_id: str
    status: str
    request_path: str
    response_path: str
    raw_video_path: str = ""
    error_message: str = ""
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def touch(self, status: str | None = None) -> None:
        if status:
            self.status = status
        self.updated_at = utc_now()

    def to_dict(self) -> dict:
        return asdict(self)
