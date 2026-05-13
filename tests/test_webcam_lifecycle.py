import inspect
import types


def test_controller_imports_and_init_without_cv2_or_camera(monkeypatch):
    import rinovision.capture.webcam as webcam

    calls = {"import_cv2": 0}
    monkeypatch.setattr(webcam, "_import_cv2", lambda: calls.__setitem__("import_cv2", calls["import_cv2"] + 1))
    controller = webcam.WebcamPreviewController(camera_id=0)
    assert controller.is_running() is False
    assert calls["import_cv2"] == 0


def test_controller_start_lazy_loads_cv2_and_opens_once(monkeypatch):
    import rinovision.capture.webcam as webcam

    calls = {"captures": 0}

    class FakeCapture:
        def __init__(self, camera_id):
            calls["captures"] += 1
            self.camera_id = camera_id

        def isOpened(self):
            return True

        def read(self):
            return True, "frame"

        def release(self):
            pass

    fake_cv2 = types.SimpleNamespace(VideoCapture=FakeCapture)
    monkeypatch.setattr(webcam, "_import_cv2", lambda: fake_cv2)
    controller = webcam.WebcamPreviewController(camera_id=1)

    assert controller.start()["ok"] is True
    assert controller.start()["ok"] is True
    assert calls["captures"] == 1


def test_controller_read_frame_reads_one_frame(monkeypatch):
    import rinovision.capture.webcam as webcam

    calls = {"reads": 0}

    class FakeCapture:
        def isOpened(self):
            return True

        def read(self):
            calls["reads"] += 1
            return True, f"frame-{calls['reads']}"

        def release(self):
            pass

    fake_cv2 = types.SimpleNamespace(VideoCapture=lambda _camera_id: FakeCapture())
    monkeypatch.setattr(webcam, "_import_cv2", lambda: fake_cv2)
    controller = webcam.WebcamPreviewController()
    controller.start()

    assert controller.read_frame() == "frame-1"
    assert calls["reads"] == 1


def test_controller_stop_releases_and_is_idempotent(monkeypatch):
    import rinovision.capture.webcam as webcam

    calls = {"releases": 0}

    class FakeCapture:
        def isOpened(self):
            return True

        def read(self):
            return True, object()

        def release(self):
            calls["releases"] += 1

    fake_cv2 = types.SimpleNamespace(VideoCapture=lambda _camera_id: FakeCapture())
    monkeypatch.setattr(webcam, "_import_cv2", lambda: fake_cv2)
    controller = webcam.WebcamPreviewController()
    controller.start()

    assert controller.stop()["ok"] is True
    assert controller.stop()["ok"] is True
    assert calls["releases"] == 1
    assert controller.is_running() is False


def test_preview_code_has_no_recursive_preview_call():
    import rinovision.capture.webcam as webcam

    source = inspect.getsource(webcam.preview_webcam)
    assert source.count("preview_webcam(") == 1
    assert "WebcamPreviewController" in source


def test_gui_webcam_modules_import_without_camera():
    import importlib

    for module_name in [
        "windows.webcam_window",
        "windows.webcam_window_refactor",
        "windows.webcam_window_refactor_v2",
        "windows.webcam_window_refactorv3",
        "windows.webcam_window_refactorv4",
    ]:
        module = importlib.import_module(module_name)
        assert hasattr(module, "WebcamWindow")
