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

WEBCAM_WINDOW_IMPORTS = [
    "windows.webcam_window",
    "windows.webcam_window_refactor",
    "windows.webcam_window_refactor_v2",
    "windows.webcam_window_refactorv3",
    "windows.webcam_window_refactorv4",
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


def webcam_capability() -> dict:
    try:
        from rinovision.capture.webcam import WebcamCaptureAdapter, WebcamPreviewController, check_webcam_dependencies

        adapter = WebcamCaptureAdapter()
        adapter_status = adapter.status()
        preview_dependencies = check_webcam_dependencies()
        controller_import = {"ok": True, "class": WebcamPreviewController.__name__}
    except Exception as exc:
        adapter_status = {"available": False, "import_error": f"{type(exc).__name__}: {exc}"}
        preview_dependencies = {"available": False, "message": f"{type(exc).__name__}: {exc}"}
        controller_import = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    return {
        "adapter_status": adapter_status,
        "preview_controller_import": controller_import,
        "preview_dependencies": preview_dependencies,
        "cv2_available": importlib.util.find_spec("cv2") is not None,
        "mediapipe_available": importlib.util.find_spec("mediapipe") is not None,
        "pyside6_available": importlib.util.find_spec("PySide6") is not None,
        "hardware_probe_run": False,
        "legacy_manager_imports": {
            "managers.webcam_manager": import_status("managers.webcam_manager"),
            "managers.webcam_manager_refactorv1": import_status("managers.webcam_manager_refactorv1"),
        },
        "legacy_window_imports": {name: import_status(name) for name in WEBCAM_WINDOW_IMPORTS},
    }


def ai_video_creator_capability() -> dict:
    package_status = import_status("rinovision.ai_video_creator")
    local_status = import_status("rinovision.ai_video_creator.providers.local_stub")
    openai_status = import_status("rinovision.ai_video_creator.providers.openai_video")
    openai_capability = {"dry_run": True, "api_key_present": bool(os.getenv("OPENAI_API_KEY"))}
    if openai_status["ok"]:
        try:
            from rinovision.ai_video_creator.providers.openai_video import OpenAIVideoProvider

            openai_capability.update(OpenAIVideoProvider(dry_run=True).capability())
        except Exception as exc:
            openai_capability["error"] = f"{type(exc).__name__}: {exc}"
    return {
        "package_import": package_status,
        "local_stub_provider_import": local_status,
        "openai_video_provider_import": openai_status,
        "openai_video_provider": openai_capability,
    }


def studio_composer_capability() -> dict:
    package_status = import_status("rinovision.studio_composer")
    model_status = import_status("rinovision.studio_composer.models")
    media_loader_status = import_status("rinovision.studio_composer.media_loader")
    video_preview_status = import_status("rinovision.studio_composer.video_preview")
    ui_status = import_status("rinovision.studio_composer.ui.studio_window")
    storage_status = {"ok": False}
    try:
        from rinovision.studio_composer.storage import get_studio_root, studio_path

        root = get_studio_root()
        storage_status = {
            "ok": True,
            "root": str(root),
            "uploads": studio_path("uploads").exists(),
            "layouts": studio_path("layouts").exists(),
            "previews": studio_path("previews").exists(),
            "reports": studio_path("reports").exists(),
        }
    except Exception as exc:
        storage_status = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    qgraphics_support = False
    if importlib.util.find_spec("PySide6") is not None:
        try:
            from PySide6.QtWidgets import QGraphicsView

            qgraphics_support = QGraphicsView is not None
        except Exception:
            qgraphics_support = False
    return {
        "package_import": package_status,
        "multilayer_model_import": model_status,
        "media_loader_import": media_loader_status,
        "video_preview_import": video_preview_status,
        "ui_import": ui_status,
        "storage": storage_status,
        "pyside6_available": importlib.util.find_spec("PySide6") is not None,
        "qgraphicsview_available": qgraphics_support,
        "camera_probe_run": False,
    }


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
            "webcam": webcam_capability(),
        },
        "ai_video_creator": ai_video_creator_capability(),
        "studio_composer": studio_composer_capability(),
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
    webcam = report["media_adapters"]["webcam"]["adapter_status"]
    webcam_preview = report["media_adapters"]["webcam"]["preview_dependencies"]
    print(f"music manager import: {'yes' if music['import_ok'] else 'no'}")
    print(f"webcam adapter available: {'yes' if webcam.get('available') else 'no'}")
    print(f"webcam preview dependency: {'yes' if webcam_preview.get('available') else 'no'}")
    print(f"cv2 available: {'yes' if report['media_adapters']['webcam'].get('cv2_available') else 'no'}")
    print(f"mediapipe available: {'yes' if report['media_adapters']['webcam'].get('mediapipe_available') else 'no'}")
    print(f"PySide6 available: {'yes' if report['media_adapters']['webcam'].get('pyside6_available') else 'no'}")
    controller = report["media_adapters"]["webcam"].get("preview_controller_import", {})
    print(f"webcam controller import: {'yes' if controller.get('ok') else 'no'}")
    if webcam.get("missing_dependencies"):
        print(f"webcam missing dependencies: {', '.join(webcam['missing_dependencies'])}")
    creator = report["ai_video_creator"]
    print(f"ai video creator import: {'yes' if creator['package_import']['ok'] else 'no'}")
    print(f"openai video dry-run: {'yes' if creator['openai_video_provider'].get('dry_run') else 'no'}")
    studio = report["studio_composer"]
    print(f"studio composer import: {'yes' if studio['package_import']['ok'] else 'no'}")
    print(f"studio composer multilayer model: {'yes' if studio['multilayer_model_import']['ok'] else 'no'}")
    print(f"studio composer media loader: {'yes' if studio['media_loader_import']['ok'] else 'no'}")
    print(f"studio composer video preview: {'yes' if studio['video_preview_import']['ok'] else 'no'}")
    print(f"studio composer storage: {'yes' if studio['storage'].get('ok') else 'no'}")
    print(f"studio composer QGraphicsView: {'yes' if studio.get('qgraphicsview_available') else 'no'}")
    print(f"report: {report['report_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
