import json
import re
import shutil
from pathlib import Path

from rinovision.core.errors import PathSafetyError
from rinovision.paths import ensure_data_dirs, safe_path

STUDIO_ROOT = "studio_composer"
STUDIO_DIRS = ("uploads", "layouts", "previews", "reports")


def get_studio_root() -> Path:
    data_root = ensure_data_dirs()
    root = safe_path(data_root, STUDIO_ROOT)
    root.mkdir(parents=True, exist_ok=True)
    for name in STUDIO_DIRS:
        safe_path(root, name).mkdir(parents=True, exist_ok=True)
    return root


def studio_path(category: str, filename: str | None = None) -> Path:
    if category not in STUDIO_DIRS:
        raise PathSafetyError(f"unknown studio composer category: {category}")
    base = safe_path(get_studio_root(), category)
    if filename is None:
        return base
    if Path(filename).name != filename:
        raise PathSafetyError("studio composer filename must not contain directories")
    return safe_path(base, filename)


def write_json(category: str, filename: str, payload: dict) -> Path:
    target = studio_path(category, filename)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return target


def read_json(category: str, filename: str) -> dict:
    return json.loads(studio_path(category, filename).read_text(encoding="utf-8"))


def sanitize_filename(filename: str) -> str:
    name = Path(filename).name
    stem = re.sub(r"[^A-Za-z0-9_. -]+", "_", Path(name).stem).strip() or "upload"
    suffix = re.sub(r"[^A-Za-z0-9.]+", "", Path(name).suffix.lower())
    return f"{stem}{suffix}"


def copy_upload(source_path: str | Path, project_id: str | None = None) -> Path:
    source = Path(source_path).expanduser().resolve()
    if not source.exists() or not source.is_file():
        raise FileNotFoundError(f"upload source not found: {source}")
    safe_name = sanitize_filename(source.name)
    if project_id:
        safe_name = sanitize_filename(f"{project_id}_{safe_name}")
    target = studio_path("uploads", safe_name)
    counter = 1
    while target.exists():
        candidate = f"{target.stem}_{counter}{target.suffix}"
        target = studio_path("uploads", candidate)
        counter += 1
    shutil.copy2(source, target)
    return target
