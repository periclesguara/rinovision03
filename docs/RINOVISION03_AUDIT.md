# RINOVISION03 Audit

## Summary

RINOVISION03 is a legacy Python/PySide6 multimedia creator app with active GUI windows, webcam/audio/screen recording managers, composition/editing modules, OpenAI assistant scripts, CrewAI/RAG experiments, patch scripts, logs, generated media folders, and duplicated refactor attempts.

## Main Entry Point

- Likely active entry: `main.py`
- Current default behavior: launches `windows.compositor_window.CompositorWindow`
- Manifest also references `windows/webcam_window_refactorv4.py` as a runtime entry for webcam experiments.

## GUI Framework

- GUI framework: PySide6
- Media/UI dependencies used by GUI code include `cv2`, `numpy`, `mediapipe`, `ffmpeg-python`, `PySide6.QtMultimedia`, and `PySide6.QtMultimediaWidgets`.

## Active Windows

- `windows/compositor_window.py`
- `windows/image_composer_window.py`
- `windows/edition_window.py`
- `windows/webcam_window.py`
- `windows/base_window.py`
- `gui/main_window.py`

## Active Managers

- `managers/audio_manager.py`
- `managers/record_manager.py`
- `managers/scene_manager.py`
- `managers/webcam_manager.py`
- `managers/editor_manager/export_manager.py`
- `managers/editor_manager/music_manager.py`
- `managers/editor_manager/subtitle_manager.py`
- `managers/editor_manager/text_effects_manager.py`

## Duplicate Webcam Implementations

- `managers/webcam_manager.py`
- `managers/webcam_manager_refactorv1.py`
- `assistente/managers/webcam_manager_refactorv1.py`
- `windows/webcam_window.py`
- `windows/webcam_window_refactor.py`
- `windows/webcam_window_refactor_v2.py`
- `windows/webcam_window_refactorv3.py`
- `windows/webcam_window_refactorv4.py`
- `assistente/windows/webcam_window_refactorv4.py`
- indexed copies under `assistente/crewai/AgenteCrewAI02/indexador/files_indexados/`

## Duplicate Assistant Implementations

- `src/assistente/`
- `src/components/openai_client.py`
- `assistente/AgenteCrewAI02/`
- `assistente/crewai/AgenteCrewAI02/`
- `assistente/crewai/assistente/crewai/`
- root scripts such as `usar_assistente.py`, `criar_assistente_rino.py`, and upload/indexing helpers.

## Patch Scripts

- `patch/patch_compositor.py` changes a window title dynamically and is likely obsolete after an official compositor path exists.
- `scripts/patch_edition_window.sh` and `scripts/patch_compositor_caption.sh` mutate source files with `sed`; keep documented but do not run automatically.
- Root `fix_*.sh` scripts appear to be one-off repair scripts and should remain untouched until references are proven obsolete.

## Runtime Folders To Keep Out Of Git

- `logs/`
- `output/`
- `frames/`
- `music/generated/`
- `data/output/`
- `data/tmp/`
- `data/frames/`
- `data/audio/generated/`
- `data/video/generated/`
- `data/exports/`
- `data/reports/`

## Business Logic Candidates

- `managers/*.py`
- `managers/editor_manager/*.py`
- `utils/image_processing.py`
- `utils/background_removal.py`
- `utils/file_manager.py`
- `src/assistente/rino_assistente.py`
- `assistente/crewai/*`

## UI-Only Candidates

- `gui/main_window.py`
- `gui/splash_screen.py`
- `windows/*.py`
- `components/*.py`

## Core Services To Extract

- capture services: audio, webcam, screen recording
- editing services: scene composition, subtitles, music, text effects, export
- artifact registry: project outputs and reports
- assistant provider abstraction
- AI video provider abstraction

## Missing Dependency Risks

- `pytest` was missing in the active environment.
- `PySide6` was missing in the active environment, although listed in `requirements.txt`.
- `openai`, `python-dotenv`, `crewai`, `langchain`, `langchain_openai`, `langchain_community`, `faiss`, `moviepy`, and some media packages are referenced but not consistently listed in the root requirements.

## Security Risks

- `.env` exists and must remain ignored.
- Hardcoded API secrets were detected in legacy files/logs. Values are intentionally not reproduced here.
- Some assistant modules instantiate OpenAI clients at import time; this should be replaced with explicit provider calls.
- RAG loading uses dangerous deserialization in one legacy file.

## Likely Broken Imports

- `windows/edition_window.py` imports `managers.subtitle_manager`, but subtitle manager appears under `managers/editor_manager/subtitle_manager.py`.
- `windows/webcam_window_refactorv4.py` imports `webcam_manager_refactorv1` via path manipulation.
- Several CrewAI/LangChain modules rely on dependencies not present in root requirements.
- Indexed files under `assistente/crewai/AgenteCrewAI02/indexador/files_indexados/` include at least one syntactically invalid Python file.

## Target Architecture

Use the new `rinovision/` package as the stable foundation:

- `rinovision.core`: project, pipeline, artifact registry
- `rinovision.paths`: safe runtime storage under `data/`
- `rinovision.capture`: adapters over legacy capture managers
- `rinovision.editing`: editing pipeline and adapters
- `rinovision.ai_video`: provider-neutral raw AI video generation flow
- `rinovision.assistant`: provider-neutral assistant layer
- `rinovision.ui`: compatibility wrappers for legacy GUI
