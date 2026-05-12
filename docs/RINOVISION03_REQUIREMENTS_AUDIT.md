# RINOVISION03 Requirements Audit

## Root Requirements Observed

The root `requirements.txt` contains GUI/media/scientific packages including PySide6, OpenCV, mediapipe, numpy, scipy, matplotlib, pydub, sounddevice, soundfile, and ffmpeg-python.

## Missing Or Under-Specified Imports

- `pytest`: required by tests.
- `openai`: imported by assistant scripts.
- `python-dotenv`: imported by assistant scripts; present only in `src/components/requirements.txt`.
- `moviepy`: imported by text effects manager.
- `crewai`, `langchain`, `langchain_openai`, `langchain_community`, FAISS-related packages: used by CrewAI/RAG experiments.

## Maybe Unused Or Heavy

- `jax`, `jaxlib`, `matplotlib`, and `sentencepiece` may be experimental or transitive; keep in original requirements until import usage is reviewed.

## Grouping Recommendation

- `requirements-core.txt`: base GUI/media app runtime.
- `requirements-dev.txt`: tests and developer tools.
- `requirements-ai.txt`: OpenAI/CrewAI/RAG optional dependencies.

The original `requirements.txt` was preserved.
