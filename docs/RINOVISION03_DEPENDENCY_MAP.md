# RINOVISION03 Dependency Map

## GUI

- PySide6
- shiboken6

## Capture And Media

- opencv-python / opencv-contrib-python
- numpy
- mediapipe
- sounddevice
- soundfile
- pydub
- ffmpeg-python
- external `ffmpeg` / `ffprobe`

## Editing

- moviepy is imported by `managers/editor_manager/text_effects_manager.py` but is not in root `requirements.txt`.

## AI / Assistant

- openai is used by assistant scripts but is not in root `requirements.txt`.
- python-dotenv is used by assistant scripts but is not in root `requirements.txt`; it appears in `src/components/requirements.txt`.
- crewai/langchain/langchain_openai/langchain_community/faiss are referenced by assistant experiments and manifest.

## Testing

- pytest is required for tests but was missing from the active shell.
