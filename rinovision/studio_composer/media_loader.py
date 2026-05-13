import re
from pathlib import Path

from rinovision.core.errors import PathSafetyError
from rinovision.studio_composer.models import ComposerLayer
from rinovision.studio_composer.storage import copy_upload

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm"}


def detect_media_type(path: str | Path) -> str:
    suffix = Path(path).suffix.lower()
    if suffix in IMAGE_EXTENSIONS:
        return "image"
    if suffix in VIDEO_EXTENSIONS:
        return "video"
    return "unsupported"


def classify_media(path: str | Path) -> str:
    media_type = detect_media_type(path)
    if media_type == "unsupported":
        raise ValueError(f"unsupported studio composer media type: {Path(path).suffix.lower()}")
    return media_type


def validate_media_file(path: str | Path) -> Path:
    candidate = Path(path).expanduser()
    if ".." in candidate.parts:
        raise PathSafetyError("media path must not contain traversal segments")
    resolved = candidate.resolve()
    if not resolved.exists() or not resolved.is_file():
        raise FileNotFoundError(f"media file not found: {resolved}")
    classify_media(resolved)
    return resolved


def _safe_layer_name(media_type: str, path: Path) -> str:
    stem = re.sub(r"[^A-Za-z0-9_. -]+", "_", path.stem).strip() or media_type.title()
    return f"{media_type.title()} - {stem}"


def import_media_file(path: str | Path, project_id: str) -> ComposerLayer:
    source = validate_media_file(path)
    media_type = classify_media(source)
    target = copy_upload(source, project_id=project_id)
    default_width, default_height = (640, 360) if media_type == "video" else (640, 360)
    metadata = {}
    if media_type == "image":
        metadata["adjustments"] = {"brightness": 0, "contrast": 0, "crop": None, "fit_mode": "contain"}
    if media_type == "video":
        metadata["preview_mode"] = "first_frame"
    return ComposerLayer(
        name=_safe_layer_name(media_type, source),
        layer_type=media_type,
        source_path=str(target),
        x=100,
        y=80,
        width=default_width,
        height=default_height,
        z_index=1,
        metadata=metadata,
    )


def import_multiple_media_files(paths: list[str | Path], project_id: str) -> list[ComposerLayer]:
    return [import_media_file(path, project_id) for path in paths]


def import_base_media(source_path: str | Path) -> dict:
    media_type = classify_media(source_path)
    target = copy_upload(source_path)
    return {"type": media_type, "path": str(target)}
