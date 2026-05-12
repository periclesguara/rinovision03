#!/usr/bin/env python3
import importlib
import json
import os
from pathlib import Path
import platform
import py_compile
import shutil
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rinovision.paths import CATEGORIES, ensure_data_dirs, get_data_root


LEGACY_IMPORTS = [
    "managers.audio_manager",
    "managers.record_manager",
    "managers.scene_manager",
    "managers.webcam_manager",
    "managers.webcam_manager_refactorv1",
    "managers.editor_manager.export_manager",
    "managers.editor_manager.music_manager",
    "managers.editor_manager.subtitle_manager",
    "managers.editor_manager.text_effects_manager",
]


def import_status(module_name: str) -> dict:
    try:
        module = importlib.import_module(module_name)
        public = [name for name in dir(module) if not name.startswith("_")]
        return {"ok": True, "public": public[:30]}
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


def music_manager_capability() -> dict:
    status = import_status("managers.editor_manager.music_manager")
    capability = {
        "import_ok": status["ok"],
        "ffmpeg_available": shutil.which("ffmpeg") is not None,
        "function_available": False,
        "adapter_available": False,
    }
    if status["ok"]:
        module = importlib.import_module("managers.editor_manager.music_manager")
        capability["function_available"] = callable(getattr(module, "inserir_musica_de_fundo", None))
    try:
        from rinovision.editing.music import MusicAdapter

        adapter = MusicAdapter()
        adapter_status = adapter.status()
        capability["adapter_available"] = adapter_status.get("available", False)
        capability["adapter_status"] = adapter_status
    except Exception as exc:
        capability["adapter_status"] = {"available": False, "import_error": f"{type(exc).__name__}: {exc}"}
    return capability


def gitignore_contains(pattern: str) -> bool:
    gitignore = ROOT / ".gitignore"
    return gitignore.exists() and pattern in gitignore.read_text(encoding="utf-8")


def compile_foundation() -> dict:
    failures = []
    for folder in ("rinovision", "scripts", "tests"):
        for path in (ROOT / folder).rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            try:
                py_compile.compile(str(path), doraise=True)
            except Exception as exc:
                failures.append({"path": str(path.relative_to(ROOT)), "error": str(exc)})
    return {"ok": not failures, "failures": failures[:50], "failure_count": len(failures)}


def run_healthcheck() -> dict:
    data_root = ensure_data_dirs()
    report = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "project_root": str(ROOT),
        "data_root": str(data_root),
        "required_folders": {name: (data_root / rel).exists() for name, rel in CATEGORIES.items()},
        "ffmpeg_available": shutil.which("ffmpeg") is not None,
        "ffprobe_available": shutil.which("ffprobe") is not None,
        "legacy_imports": {name: import_status(name) for name in LEGACY_IMPORTS},
        "media_adapters": {
            "music_manager": music_manager_capability(),
        },
        "rinovision_import": import_status("rinovision"),
        "env_file_exists": (ROOT / ".env").exists(),
        "env_example_exists": (ROOT / ".env.example").exists(),
        "tests_folder_exists": (ROOT / "tests").exists(),
        "docs_folder_exists": (ROOT / "docs").exists(),
        "gitignore_runtime_rules": {
            ".env": gitignore_contains(".env"),
            "*.env": gitignore_contains("*.env"),
            ".env.*": gitignore_contains(".env.*"),
            "!.env.example": gitignore_contains("!.env.example"),
            "data/output/": gitignore_contains("data/output/"),
            "data/tmp/": gitignore_contains("data/tmp/"),
            "data/reports/*.json": gitignore_contains("data/reports/*.json"),
            "data/edited_videos/": gitignore_contains("data/edited_videos/"),
            "data/ai_video/generated_raw/": gitignore_contains("data/ai_video/generated_raw/"),
            "data/ai_video/provider_responses/": gitignore_contains("data/ai_video/provider_responses/"),
            "logs/": gitignore_contains("logs/"),
            "output/": gitignore_contains("output/"),
            "frames/": gitignore_contains("frames/"),
            "venv/": gitignore_contains("venv/"),
        },
        "compile": compile_foundation(),
    }
    output_path = get_data_root() / "reports" / "healthcheck_report.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    report["report_path"] = str(output_path)
    return report


def main() -> int:
    report = run_healthcheck()
    print("RinoVision healthcheck")
    print(f"Python: {platform.python_version()}")
    print(f"Project root: {report['project_root']}")
    print(f"Data root: {report['data_root']}")
    print(f"ffmpeg: {'yes' if report['ffmpeg_available'] else 'no'}")
    print(f"ffprobe: {'yes' if report['ffprobe_available'] else 'no'}")
    print(f".env exists: {'yes' if report['env_file_exists'] else 'no'}")
    print(f".env.example exists: {'yes' if report['env_example_exists'] else 'no'}")
    print(f"tests folder: {'yes' if report['tests_folder_exists'] else 'no'}")
    print(f"docs folder: {'yes' if report['docs_folder_exists'] else 'no'}")
    print(f"compile ok: {'yes' if report['compile']['ok'] else 'no'}")
    music = report["media_adapters"]["music_manager"]
    print(f"music manager import: {'yes' if music['import_ok'] else 'no'}")
    print(f"report: {report['report_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
