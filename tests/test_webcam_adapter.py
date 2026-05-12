import importlib
import types


def test_webcam_adapter_imports_without_camera_access(monkeypatch):
    calls = {"video_capture": 0}

    class FakeVideoCapture:
        def __init__(self, *_args, **_kwargs):
            calls["video_capture"] += 1
            raise AssertionError("VideoCapture must not be called during adapter import/status")

    fake_cv2 = types.SimpleNamespace(VideoCapture=FakeVideoCapture)
    fake_numpy = types.SimpleNamespace()
    fake_mediapipe = types.SimpleNamespace(
        solutions=types.SimpleNamespace(
            selfie_segmentation=types.SimpleNamespace(SelfieSegmentation=object)
        )
    )
    monkeypatch.setitem(__import__("sys").modules, "cv2", fake_cv2)
    monkeypatch.setitem(__import__("sys").modules, "numpy", fake_numpy)
    monkeypatch.setitem(__import__("sys").modules, "mediapipe", fake_mediapipe)

    module = importlib.import_module("rinovision.capture.webcam")
    adapter = module.WebcamCaptureAdapter()
    status = adapter.status()

    assert "available" in status
    assert calls["video_capture"] == 0


def test_missing_webcam_dependencies_do_not_crash_adapter(monkeypatch):
    module = importlib.import_module("rinovision.capture.webcam")
    monkeypatch.setattr(module, "_dependency_available", lambda _name: False)

    adapter = module.WebcamCaptureAdapter()
    status = adapter.status()

    assert status["available"] is False
    assert "opencv-python" in status["missing_dependencies"]
    assert "mediapipe" in status["missing_dependencies"]


def test_healthcheck_reports_webcam_capability():
    from scripts.rinovision_healthcheck import run_healthcheck

    report = run_healthcheck()
    webcam = report["media_adapters"]["webcam"]["adapter_status"]
    assert "available" in webcam
    assert "message" in webcam or "import_error" in webcam


def test_main_demos_still_run_after_webcam_hardening():
    import main

    assert main.run_ai_video_demo() == 0
    assert main.run_editing_demo() == 0
