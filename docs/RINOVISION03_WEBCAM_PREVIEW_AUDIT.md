# RINOVISION03 Webcam Preview Audit

## Stable Pattern Found

The stable legacy pattern is the PySide6 timer-driven preview used by the webcam windows:

- `windows/webcam_window.py`
- `windows/webcam_window_refactor.py`
- `windows/webcam_window_refactor_v2.py`
- `windows/webcam_window_refactorv3.py`
- `windows/webcam_window_refactorv4.py`

These windows use `QTimer` to call `update_frame()`. Each timer tick reads one frame and returns control to the event loop. This avoids blocking GUI execution and avoids uncontrolled infinite camera loops.

## Canonical Candidate

`windows/webcam_window_refactorv4.py` appears to be the best legacy reference because it is named as the more recent refactor and has a focused preview/effects UI. It should remain legacy-compatible, while the canonical lifecycle should now live in `rinovision.capture.webcam.WebcamPreviewController`.

## Unsafe Looping Patterns

No legacy PySide6 webcam window currently uses a `while True` preview loop. The only loop-like preview behavior belongs in the CLI preview path, where it is acceptable only when started explicitly by `python main.py --webcam-preview` and paired with reliable release/cleanup.

Uncontrolled GUI loops remain forbidden. GUI preview must be timer/event-driven.

## Camera Creation

The legacy managers create camera objects in their constructors:

- `managers/webcam_manager.py`: `WebcamManager.__init__()` opens `cv2.VideoCapture(0)`.
- `managers/webcam_manager_refactorv1.py`: `WebcamManager.__init__()` opens `cv2.VideoCapture(0)`.

They do not open cameras during module import after import-safety hardening, but constructing these legacy classes accesses camera hardware. The safer canonical lifecycle is:

```text
controller = WebcamPreviewController(camera_id=0)
controller.start()
frame = controller.read_frame()
controller.stop()
```

## Timer/Event-Driven Files

- `windows/webcam_window.py`
- `windows/webcam_window_refactor.py`
- `windows/webcam_window_refactor_v2.py`
- `windows/webcam_window_refactorv3.py`
- `windows/webcam_window_refactorv4.py`

## Release Behavior

The legacy webcam windows call manager release methods in `closeEvent()`. The canonical controller also makes `stop()` idempotent, releases the camera safely, and can be called from close handlers, stop buttons, or CLI cleanup.

## Canonical Lifecycle

Use `rinovision.capture.webcam.WebcamPreviewController` as the canonical runtime lifecycle:

- no camera access in import;
- no camera access in `__init__`;
- `start()` opens one `cv2.VideoCapture`;
- repeated `start()` calls do not create additional captures;
- `read_frame()` reads one frame only;
- `stop()` releases resources and is safe to call repeatedly;
- CLI preview closes on `Q` or `ESC`;
- GUI preview should use `QTimer` and call `read_frame()` once per tick.
