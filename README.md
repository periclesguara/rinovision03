# RinoVision03

## What Is RinoVision

RinoVision is a Python desktop creator-tech pipeline for capture, composition, editing, subtitles, music, text effects, exports, and AI-assisted video workflows.

## Current Status

This repository is a legacy rescue and product foundation. The existing PySide6 GUI and managers are preserved, while a new `rinovision/` package provides safer paths, project manifests, artifact tracking, pipeline states, AI Video Maker stubs, editing stubs, assistant adapters, and health checks.

## Legacy Baseline

The current legacy entry point is still `main.py`, which launches the existing compositor GUI by default. Legacy folders such as `windows/`, `managers/`, `components/`, `utils/`, `assistente/`, and `test/` were not deleted.

## Safe Startup

```bash
python main.py
python main.py --safe-mode
python main.py --healthcheck
python main.py --ai-video-demo
python main.py --ai-video-creator-demo
python main.py --editing-demo
```

`python main.py` requires GUI dependencies such as PySide6. `--safe-mode` uses the new compatibility adapter and falls back to a CLI message if GUI dependencies are unavailable. `--safe-foundation` remains as an alias.

## Healthcheck

```bash
python scripts/rinovision_healthcheck.py
python main.py --healthcheck
```

The healthcheck writes `data/reports/healthcheck_report.json` and checks Python, project/data roots, required folders, ffmpeg/ffprobe, legacy manager imports, new package import, `.env` existence without printing secrets, `.gitignore` runtime rules, and compile status.

## Data Folders

Runtime artifacts belong under `data/`, including:

- `data/input/`
- `data/output/`
- `data/tmp/`
- `data/audio/`
- `data/video/`
- `data/images/`
- `data/frames/`
- `data/subtitles/`
- `data/exports/`
- `data/reports/`
- `data/projects/`
- `data/ai_video/`
- `data/edited_videos/`
- `data/edit_plans/`

Fixed project resources stay under `assets/`.

## AI Video Maker Concept

AI Video Maker currently uses provider-neutral stubs. It creates script, storyboard, prompts, provider request/response JSON, and raw AI video placeholders. Raw generated AI video is never treated as final export; it is routed into the editing pipeline.

Demo:

```bash
python main.py --ai-video-demo
```

## AI Video Creator Architecture

`rinovision/ai_video_creator/` is the dedicated brief-to-video-substrate pipeline. It turns a creative brief into a deterministic local script, storyboard, provider prompts, a provider job, a raw generated video placeholder, an editing import, and a local social package draft.

Workflow:

```text
brief -> script -> storyboard -> prompts -> provider job -> raw substrate -> editing pipeline -> social package draft
```

Local stub mode makes no external API calls and writes JSON/text/placeholders under `data/ai_video_creator/`. The OpenAI video provider exists only as a dry-run adapter for now; it imports without `OPENAI_API_KEY`, does not call the network in tests, and does not store API keys in artifacts. AI-generated video is raw audiovisual substrate, not the final product, and must be routed through editing before export. Social packages are local drafts for manual upload to Instagram, Facebook, and YouTube; there is no automatic publishing.

Demo:

```bash
python main.py --ai-video-creator-demo
```

## Editing Pipeline Concept

The editing foundation accepts capture, upload, AI video, or editing-only sources. It can probe video with `ffprobe` when available, create an edit plan, create edited video placeholders, generate subtitle/thumbnail placeholders, and create export package manifests.

Demo:

```bash
python main.py --editing-demo
```

## Webcam Preview

```bash
python main.py --webcam-probe
python main.py --webcam-preview
python main.py --webcam-preview --camera-id 1
```

Webcam preview requires `opencv-python`. Use `--webcam-probe` to list available camera IDs first. The preview is read-only and live only; it does not record or write video files. Press `Q` or `ESC` to close the preview window.

## Security Notes

Do not commit `.env`. API providers must be configured through environment variables and provider adapters. Legacy hardcoded API key patterns were redacted during the safety pass; rotate any keys that may have appeared in old logs or history.

## Development Commands

```bash
python scripts/rinovision_healthcheck.py
python -m compileall rinovision scripts tests
pytest -q
python main.py
python main.py --safe-mode
python main.py --ai-video-demo
python main.py --ai-video-creator-demo
python main.py --editing-demo
python main.py --webcam-probe
python main.py --studio-composer-demo-layout
python main.py --studio-composer-demo-multilayer
```

Current validation target is the new foundation, not the full legacy tree. Some legacy modules still require optional GUI/media dependencies.

Optional grouped requirements were added:

- `requirements-core.txt`
- `requirements-dev.txt`
- `requirements-ai.txt`

The original `requirements.txt` is preserved.

## Webcam Lifecycle

The canonical webcam runtime lifecycle is `WebcamPreviewController` in `rinovision.capture.webcam`:

```text
start() -> read_frame() by CLI loop or GUI timer -> stop()
```

The controller does not open the camera during import or construction. GUI webcam previews must use timer/event-driven frame updates, not blocking `while True` loops. CLI preview is explicit only:

```bash
python main.py --webcam-probe
python main.py --webcam-preview
python main.py --webcam-preview --camera-id 1
```

Press `Q` or `ESC` to close the CLI preview. The command is read-only and does not record video.

## Studio Composer

Studio Composer is the OBS-like preparation screen for composing a scene before recording. It provides a canvas for multiple image layers, multiple video layers, and one independent webcam overlay layer. Layers can be selected, moved, resized directly with corner handles, scaled with `Scale +` / `Scale -`, ordered forward/backward, locked, and saved as scene layout JSON for a later recording step.

Studio Composer now uses OBS-style numbered layer slots:

- Layer 1: foreground / first plane
- Layer 2: second plane, behind Layer 1
- Layer 3: optional background, behind Layer 2
- Layer 4: optional deeper background, behind Layer 3

These slots are visual depth slots, not screen quadrants or regions. A source assigned to any slot can still be moved anywhere on the canvas using its `x`/`y` position. Webcam, image, and video sources can be assigned to any slot. Empty slots are allowed. Lock freezes the final positions, sizes, slots, and order before a later recording step.

Commands:

```bash
python main.py --studio-composer-demo-layout
python main.py --studio-composer-demo-multilayer
python main.py --studio-composer-debug-scene
python main.py --studio-composer
```

The demo and debug layout commands are headless and safe for CI. The GUI command opens the PySide6 Studio Composer window. Image/video uploads are copied into `data/studio_composer/uploads/`; video layers show a first-frame preview and can be played/paused with the selected-layer `Play/Pause` control. Slot dropdowns change actual source depth through `QGraphicsItem.setZValue()` while preserving `x`/`y`. This module does not record video yet; it saves layout metadata under `data/studio_composer/layouts/`. Webcam preview still follows the controlled lifecycle and opens only after the user enables it in the composer.

Webcam enhancement controls are available for the selected webcam layer: `Bright +`, `Bright -`, `Contrast +`, `Contrast -`, `Sat +`, `Sat -`, `Mirror`, and `Reset Cam`. These are software adjustments. Lighting still matters: use soft front light, avoid backlight, keep the camera near eye level, use a clean background, and avoid strong shadows.
