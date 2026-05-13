# RINOVISION03 Import Audit

Importability depends on optional GUI/media dependencies. The new `rinovision` package catches legacy import failures in adapters and falls back to stubs where possible.

## Legacy Manager Risks

- `managers.audio_manager`: requires `sounddevice`, `soundfile`
- `managers.record_manager`: requires `PySide6`
- `managers.scene_manager`: requires `ffmpeg-python`
- `managers.webcam_manager`: imports safely; creating `WebcamManager()` still requires `cv2`, `numpy`, `mediapipe`, and camera hardware
- `managers.editor_manager.text_effects_manager`: requires `moviepy`

Run `python scripts/rinovision_healthcheck.py` for the current machine-specific import report.

## Current Healthcheck Import Results

- `managers.audio_manager`: fails in the current shell because `sounddevice` is missing.
- `managers.record_manager`: fails in the current shell because `PySide6` is missing.
- `managers.scene_manager`: fails in the current shell because `ffmpeg-python` is missing as import package `ffmpeg`.
- `managers.webcam_manager`: imports successfully after lazy dependency hardening.
- `managers.webcam_manager_refactorv1`: imports successfully after lazy dependency hardening.
- `windows.webcam_window*`: import successfully after PySide6/cv2 manager imports were made lazy; creating/showing windows still requires GUI dependencies.
- `managers.editor_manager.export_manager`: imports successfully.
- `managers.editor_manager.music_manager`: imports successfully after removing its import-time file creation side effect.
- `managers.editor_manager.subtitle_manager`: imports successfully.
- `managers.editor_manager.text_effects_manager`: fails in the current shell because `moviepy` is missing.

The new adapters do not crash at import time; they report unavailable legacy backends through stub status data.

## Webcam Import Safety

Webcam-related legacy imports were hardened:

- `managers/webcam_manager.py` no longer imports `cv2`, `numpy`, or `mediapipe` at module import time.
- `managers/webcam_manager_refactorv1.py` no longer imports `cv2`, `numpy`, or `mediapipe` at module import time.
- `windows/webcam_window.py` and refactor variants no longer require PySide6/cv2 at module import time.
- Importing webcam modules does not open camera hardware, start timers, launch GUI, or start threads.
- `rinovision.capture.webcam.WebcamCaptureAdapter` reports `available`, `missing_dependencies`, and `message`.

Current healthcheck result in this shell: webcam imports are safe. Runtime webcam capability depends on optional packages and camera hardware; healthcheck reports dependency availability without opening the camera.

## Webcam Preview Lifecycle

The canonical preview lifecycle is now `rinovision.capture.webcam.WebcamPreviewController`:

- `start()` opens the camera explicitly;
- `read_frame()` reads a single frame;
- `stop()` releases the camera and can be called repeatedly;
- no camera access happens during import or controller construction;
- PySide6 GUI windows should use `QTimer` to call one frame read per tick;
- blocking `while True` loops are forbidden inside GUI code.

Manual CLI preview:

```bash
python main.py --webcam-probe
python main.py --webcam-preview
python main.py --webcam-preview --camera-id 1
```

## Music Manager Fix

`managers/editor_manager/music_manager.py` previously executed code at import time that attempted to create `/mnt/data/music_manager.py`. It is now a normal library module:

- no file creation on import;
- no directory scanning on import;
- no playback, rendering, hardware initialization, or GUI startup on import;
- ffmpeg is invoked only when `inserir_musica_de_fundo(...)` is called explicitly;
- `rinovision.editing.music.MusicAdapter` can report backend availability safely.
