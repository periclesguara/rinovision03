# RINOVISION03 Import Audit

Importability depends on optional GUI/media dependencies. The new `rinovision` package catches legacy import failures in adapters and falls back to stubs where possible.

## Legacy Manager Risks

- `managers.audio_manager`: requires `sounddevice`, `soundfile`
- `managers.record_manager`: requires `PySide6`
- `managers.scene_manager`: requires `ffmpeg-python`
- `managers.webcam_manager`: requires `cv2`, `numpy`, `mediapipe`
- `managers.editor_manager.text_effects_manager`: requires `moviepy`

Run `python scripts/rinovision_healthcheck.py` for the current machine-specific import report.

## Current Healthcheck Import Results

- `managers.audio_manager`: fails in the current shell because `sounddevice` is missing.
- `managers.record_manager`: fails in the current shell because `PySide6` is missing.
- `managers.scene_manager`: fails in the current shell because `ffmpeg-python` is missing as import package `ffmpeg`.
- `managers.webcam_manager`: fails in the current shell because `cv2` is missing.
- `managers.webcam_manager_refactorv1`: fails in the current shell because `cv2` is missing.
- `managers.editor_manager.export_manager`: imports successfully.
- `managers.editor_manager.music_manager`: fails at import time because the legacy file writes to `/mnt/data/music_manager.py`.
- `managers.editor_manager.subtitle_manager`: imports successfully.
- `managers.editor_manager.text_effects_manager`: fails in the current shell because `moviepy` is missing.

The new adapters do not crash at import time; they report unavailable legacy backends through stub status data.
