import json
import subprocess
import sys


def test_webcam_overlay_does_not_access_camera_until_start(monkeypatch):
    calls = []

    class FakePreview:
        def __init__(self, camera_id=0):
            self.camera_id = camera_id
            calls.append(("init", camera_id))

        def start(self):
            calls.append(("start", self.camera_id))
            return {"ok": True}

        def read_frame(self):
            return None

        def stop(self):
            calls.append(("stop", self.camera_id))
            return {"ok": True}

        def get_status(self):
            return {"running": False}

    monkeypatch.setattr("rinovision.studio_composer.webcam_overlay.WebcamPreviewController", FakePreview)
    from rinovision.studio_composer.webcam_overlay import WebcamOverlayController

    overlay = WebcamOverlayController(camera_id=2)
    assert calls == [("init", 2)]
    overlay.start_preview()
    assert calls == [("init", 2), ("start", 2)]


def test_demo_layout_command_works_without_gui():
    completed = subprocess.run(
        [sys.executable, "main.py", "--studio-composer-demo-layout"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert "Studio Composer demo layout complete" in completed.stdout
    assert "recording: not enabled" in completed.stdout


def test_healthcheck_reports_studio_composer():
    from scripts.rinovision_healthcheck import run_healthcheck

    report = run_healthcheck()
    assert report["studio_composer"]["package_import"]["ok"] is True
    encoded = json.dumps(report)
    assert "OPENAI_API_KEY=" not in encoded
