import types


def test_check_webcam_dependencies_returns_dict():
    from rinovision.capture.webcam import check_webcam_dependencies

    result = check_webcam_dependencies()
    assert isinstance(result, dict)
    assert "available" in result
    assert "missing_dependencies" in result
    assert "message" in result


def test_probe_webcams_handles_missing_cv2(monkeypatch):
    import rinovision.capture.webcam as webcam

    monkeypatch.setattr(webcam, "_import_cv2", lambda: None)
    result = webcam.probe_webcams()
    assert result[0]["available"] is False
    assert "opencv-python" in result[0]["missing_dependencies"]


def test_preview_webcam_uses_camera_only_when_called_and_releases(monkeypatch):
    import rinovision.capture.webcam as webcam

    events = {"opened": 0, "released": 0, "destroyed": 0, "imshow": 0}

    class FakeCapture:
        def __init__(self, camera_id):
            events["opened"] += 1
            self.camera_id = camera_id

        def isOpened(self):
            return True

        def read(self):
            return True, object()

        def release(self):
            events["released"] += 1

    fake_cv2 = types.SimpleNamespace(
        VideoCapture=FakeCapture,
        imshow=lambda *_args: events.__setitem__("imshow", events["imshow"] + 1),
        waitKey=lambda _delay: ord("q"),
        destroyAllWindows=lambda: events.__setitem__("destroyed", events["destroyed"] + 1),
    )
    monkeypatch.setattr(webcam, "_import_cv2", lambda: fake_cv2)

    result = webcam.preview_webcam(camera_id=2)
    assert result == {"ok": True, "camera_id": 2}
    assert events == {"opened": 1, "released": 1, "destroyed": 1, "imshow": 1}


def test_main_webcam_probe_uses_probe_function(monkeypatch, capsys):
    import main
    import rinovision.capture.webcam as webcam

    monkeypatch.setattr(webcam, "probe_webcams", lambda max_devices=5: [{"camera_id": 0, "available": False}])
    assert main.run_webcam_probe() == 0
    output = capsys.readouterr().out
    assert "RinoVision Webcam Probe" in output
    assert "Camera 0: unavailable" in output


def test_existing_demos_still_work_with_webcam_preview_module():
    import main

    assert main.run_ai_video_demo() == 0
    assert main.run_editing_demo() == 0
