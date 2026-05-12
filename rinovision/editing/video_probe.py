import json
from pathlib import Path

from rinovision.utils.subprocess_tools import command_available, run_command


def probe_video(path) -> dict:
    video_path = Path(path)
    if not command_available("ffprobe"):
        return {"ok": False, "path": str(video_path), "dependency_missing": "ffprobe"}
    result = run_command(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=codec_name,width,height,r_frame_rate",
            "-of",
            "json",
            str(video_path),
        ]
    )
    if not result["ok"]:
        return {"ok": False, "path": str(video_path), "error": result["stderr"]}
    payload = json.loads(result["stdout"] or "{}")
    return {"ok": True, "path": str(video_path), "probe": payload}
