# RINOVISION03 Hardening Report

## Files Created

- `docs/RINOVISION03_HARDENING_REPORT.md`
- `data/**/.gitkeep` structural placeholders for runtime folders

## Files Modified

- `.gitignore`
- `README.md`
- `main.py`
- `scripts/rinovision_healthcheck.py`
- `docs/RINOVISION03_IMPLEMENTATION_REPORT.md`
- `docs/RINOVISION03_IMPORT_AUDIT.md`
- `docs/RINOVISION03_REFACTOR_PLAN.md`
- `rinovision/paths.py`
- `rinovision/core/errors.py`
- `rinovision/core/project.py`
- `rinovision/core/pipeline.py`
- `rinovision/core/artifact_registry.py`
- `rinovision/ai_video/raw_video_importer.py`
- `rinovision/editing/compositor.py`
- `rinovision/capture/audio.py`
- `rinovision/capture/webcam.py`
- `managers/webcam_manager.py`
- `managers/webcam_manager_refactorv1.py`
- `windows/webcam_window.py`
- `windows/webcam_window_refactor.py`
- `windows/webcam_window_refactor_v2.py`
- `windows/webcam_window_refactorv3.py`
- `windows/webcam_window_refactorv4.py`
- `rinovision/capture/screen.py`
- `rinovision/editing/exporter.py`
- `rinovision/editing/music.py`
- `rinovision/editing/subtitles.py`
- `rinovision/editing/text_effects.py`

## Tests Passed

- `pytest -q`: `9 passed in 0.40s`
- Tests cover path safety, data folder creation, pipeline transitions, project/artifact registry, AI video stub flow, editing stub flow, ffprobe missing behavior, and healthcheck secret hygiene.
- After the music manager hardening: `pytest -q` reports `12 passed in 0.48s`.
- After the webcam import-safety hardening: `pytest -q` reports `16 passed in 0.82s`.
- After the AI Video Creator module: `pytest -q` reports `24 passed`.
- After the webcam preview CLI: `pytest -q` reports `29 passed`.
- After the stable webcam lifecycle controller: lifecycle tests pass and the modern suite validates controller start/read/stop behavior without real hardware.

## Tests Failed

- None in the modern `tests/` suite.

## Commands Run

- `python scripts/rinovision_healthcheck.py`: passed
- `python -m compileall rinovision scripts tests`: passed
- `pytest -q`: passed
- `python main.py --healthcheck`: passed
- `python main.py --ai-video-demo`: passed
- `python main.py --ai-video-creator-demo`: passed
- `python main.py --editing-demo`: passed
- `python main.py --webcam-probe`: passed
- `python main.py --safe-mode`: passed with CLI fallback because GUI dependencies are unavailable in this shell
- `python -m compileall rinovision scripts tests managers`: passed after the music manager fix
- `python -m compileall rinovision scripts tests managers windows`: passed after the webcam hardening
- AI Video Creator acceptance compile/tests pass with the new module included.

## Missing Dependencies

The foundation works without these, but legacy imports report missing optional dependencies:

- `sounddevice`
- `PySide6`
- import package `ffmpeg` from `ffmpeg-python`
- `cv2` from OpenCV
- `numpy`
- `mediapipe`
- `moviepy`

## Legacy Imports That Work

- `managers.editor_manager.export_manager`
- `managers.editor_manager.music_manager`
- `managers.editor_manager.subtitle_manager`
- `managers.webcam_manager`
- `managers.webcam_manager_refactorv1`
- `windows.webcam_window`
- `windows.webcam_window_refactor`
- `windows.webcam_window_refactor_v2`
- `windows.webcam_window_refactorv3`
- `windows.webcam_window_refactorv4`

## Legacy Imports That Fail

- `managers.audio_manager`: missing `sounddevice`
- `managers.record_manager`: missing `PySide6`
- `managers.scene_manager`: missing import package `ffmpeg`
- `managers.editor_manager.text_effects_manager`: missing `moviepy`

The new adapters catch these failures and expose stub status instead of crashing at import time.

## Webcam Import Safety

Fixed. Webcam managers and webcam windows now import without opening camera hardware, starting GUI timers, importing cv2/mediapipe eagerly, or requiring PySide6 during module import. Runtime webcam use still requires optional dependencies and explicit window/manager instantiation.

Healthcheck reports:

- legacy webcam manager imports: ok
- legacy webcam window imports: ok
- webcam adapter availability
- preview dependency availability
- `cv2`, `mediapipe`, and `PySide6` availability
- preview controller import status

## Webcam Preview CLI

Added:

- `python main.py --webcam-probe`
- `python main.py --webcam-preview`
- `python main.py --webcam-preview --camera-id 1`

Preview opens camera hardware only when explicitly requested with `--webcam-preview`. Healthcheck does not probe or open camera hardware. Tests monkeypatch the preview path and do not require camera hardware, GUI windows, recording, or real `cv2` access. The preview is read-only and writes no video files; press `Q` or `ESC` to close.

Manual preview test:

```bash
python main.py --webcam-preview
python main.py --webcam-preview --camera-id 1
```

## Stable Webcam Lifecycle

Recovered as the canonical `rinovision.capture.webcam.WebcamPreviewController` lifecycle:

- `__init__()` stores configuration only and does not open hardware.
- `start()` lazy-loads OpenCV and opens one `VideoCapture`.
- repeated `start()` calls do not create additional captures.
- `read_frame()` reads one frame only.
- `stop()` releases the camera and is idempotent.
- CLI preview closes on `Q` or `ESC` and releases/destroys windows in cleanup.
- GUI preview must remain timer/event-driven with `QTimer`; uncontrolled GUI `while True` loops are forbidden.

Healthcheck reports the controller import status and dependency status without probing or opening camera hardware.

## Studio Composer Status

Upgraded. `rinovision/studio_composer/` now supports the pre-recording multilayer composition stage:

- OBS-style numbered layer slots
- Layer 1 foreground, Layer 2 second plane, Layer 3 optional background, Layer 4 deeper background
- multiple image layers
- multiple video layers with first-frame preview plus selected-layer play/pause
- empty canvas fallback
- independent webcam overlay controller using the existing safe webcam lifecycle
- webcam enhancement settings for brightness, contrast, saturation, mirror, gamma placeholder, and reset
- selected-layer move/direct-resize/scale/order metadata
- explicit image, video, webcam, and selected-layer slot controls wired to real `QGraphicsItem` z-order
- visible direct resize handles for selected image/video canvas items
- layout lock/unlock behavior
- complete scene JSON persistence under `data/studio_composer/layouts/`
- PySide6 QGraphicsView UI module for manual use
- headless demo and debug layout commands for tests and CI

Empty slots are allowed. Webcam, image, and video sources can be assigned to any slot. Lock freezes final positions, sizes, slots, and z-order before any future recording step.

Layer slots are depth slots only, not screen quadrants. Sources in Layer 1, 2, 3, or 4 remain freely movable anywhere on the canvas unless locked.

Changing a selected source from one layer slot to another preserves its `x`/`y` position and updates `computed_z_index` plus the live `QGraphicsItem.setZValue()`. Lock blocks movement, direct resize, and layer slot changes.

No recording was added in this step. Healthcheck imports Studio Composer and verifies storage without opening a GUI or camera.

Webcam enhancement is software-based. It helps tune the preview, but good lighting remains important: soft front light, no backlight, camera at eye level, clean background, and reduced shadows.

Manual GUI command:

```bash
python main.py --studio-composer
```

Headless command:

```bash
python main.py --studio-composer-demo-layout
python main.py --studio-composer-demo-multilayer
```

Acceptance after Studio Composer:

- `python scripts/rinovision_healthcheck.py`: passed
- `python -m compileall rinovision scripts tests managers windows`: passed
- `pytest -q`: 101 passed
- `python main.py --healthcheck`: passed
- `python main.py --ai-video-demo`: passed
- `python main.py --editing-demo`: passed
- `python main.py --ai-video-creator-demo`: passed
- `python main.py --webcam-probe`: passed
- `python main.py --studio-composer-demo-layout`: passed
- `python main.py --studio-composer-demo-multilayer`: passed
- `python main.py --studio-composer-debug-scene`: passed

## Music Manager Import Side Effect

Fixed. `managers/editor_manager/music_manager.py` no longer writes `/mnt/data/music_manager.py` or performs runtime work during import. It now exposes `inserir_musica_de_fundo(...)` as an explicit ffmpeg helper and invokes ffmpeg only when called.

## Main.py Status

- `python main.py` remains the default legacy compositor launcher.
- `python main.py --healthcheck` works.
- `python main.py --safe-mode` works without GUI dependencies by printing a clear fallback message.
- `python main.py --ai-video-demo` works without API keys.
- `python main.py --editing-demo` works without webcam, microphone, GUI display, or external APIs.

## AI Video Maker Stub Status

Validated. It creates script, storyboard, prompts, provider request, provider response, raw AI placeholder JSON, raw `.placeholder`, and an editing input artifact under `data/`. The project reaches `AI_VIDEO_IMPORTED_FOR_EDITING`. Raw AI video is not marked as final export.

## AI Video Creator Status

Validated. `rinovision/ai_video_creator/` creates a brief, script, storyboard, prompt set, provider job, raw video placeholder, editing import report, edit plan, and social package draft. Local stub mode makes no external calls. The OpenAI video provider is present in dry-run mode and imports without requiring `OPENAI_API_KEY`. Raw AI video is treated as substrate and routed into the Editing Pipeline before any export path.

Social package draft outputs are local/manual-upload only:

- Instagram caption
- Facebook caption
- YouTube title
- YouTube description
- hashtags
- package metadata

## Editing Pipeline Stub Status

Validated. It creates a source placeholder, video probe report, edit plan, edited video `.placeholder`, subtitle placeholder, thumbnail placeholder, and export package under `data/`. ffprobe is optional and missing dependency behavior is non-crashing.

## Recommended Next Task

Install/verify optional GUI/media dependencies in a controlled virtual environment and test `python main.py` with PySide6 available. After that, repair remaining legacy import failures for audio and text effects one module at a time.
