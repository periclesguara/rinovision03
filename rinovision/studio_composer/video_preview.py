import json
import shutil
import subprocess
from pathlib import Path

from rinovision.studio_composer.storage import studio_path


def create_video_preview_frame(video_path: str | Path, project_id: str) -> dict:
    source = Path(video_path).resolve()
    report_path = studio_path("reports", f"{project_id}_{source.stem}_video_preview.json")
    if not source.exists():
        report = {"ok": False, "error": "video source not found", "source": str(source)}
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        return report

    preview_path = studio_path("previews", f"{project_id}_{source.stem}_first_frame.jpg")
    if shutil.which("ffmpeg") is None:
        report = {
            "ok": False,
            "dependency_missing": "ffmpeg",
            "source": str(source),
            "preview_path": "",
            "preview_mode": "metadata_placeholder",
            "message": "Full playback is not implemented; ffmpeg is unavailable for first-frame extraction.",
        }
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        return report

    command = ["ffmpeg", "-y", "-i", str(source), "-frames:v", "1", str(preview_path)]
    try:
        completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=20)
        ok = completed.returncode == 0
    except Exception as exc:
        ok = False
        completed = None
        error = f"{type(exc).__name__}: {exc}"
    report = {
        "ok": ok,
        "source": str(source),
        "preview_path": str(preview_path) if ok else "",
        "preview_mode": "first_frame" if ok else "metadata_placeholder",
        "message": "First-frame preview created." if ok else "Could not create first-frame preview.",
    }
    if not ok and completed is None:
        report["error"] = error
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def create_first_frame_preview(video_path: str | Path) -> dict:
    return create_video_preview_frame(video_path, "legacy")
