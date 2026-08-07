# RinoVision03

RinoVision03 is an experimental desktop multimedia studio created by Péricles
Guará Silva. It combines a PySide6 interface, webcam/background processing,
scene composition, audio/video utilities, and an optional OpenAI text client.

This repository is a maintained prototype and portfolio artifact. It is not a
production video editor and should not be used as a security boundary or an
unattended recording service.

## Current capabilities

- PySide6 desktop shell and compositor;
- webcam capture and MediaPipe background segmentation;
- image/video base window;
- scene state and FFmpeg recording orchestration;
- OpenAI Responses API example with environment-based authentication;
- headless compile and unit-test checks in GitHub Actions.

## Requirements

- Python 3.10 or newer;
- FFmpeg available on `PATH` for recording/export features;
- a camera and PulseAudio/X11-compatible environment for the original capture
  path;
- `OPENAI_API_KEY` only when running the optional OpenAI example.

## Installation

```bash
git clone https://github.com/periclesguara/rinovision03.git
cd rinovision03
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

For development checks:

```bash
python -m pip install -e '.[dev]'
python -m compileall -q .
QT_QPA_PLATFORM=offscreen pytest -q
```

## Running the desktop prototype

```bash
python main.py
```

Hardware-dependent behavior varies by operating system. The original recording
command targets Linux, X11, and PulseAudio.

## Optional OpenAI example

The SDK reads the key from the environment. Never put a key in source code or a
committed `.env` file.

```bash
export OPENAI_API_KEY='your-local-key'
export OPENAI_MODEL='gpt-5.6'
python examples/openai_smoke.py
```

The client uses the Responses API. Tests inject a fake client and never call the
network.

## Project structure

- `windows/`: primary Qt windows;
- `components/`: reusable interface components;
- `managers/`: scene, recording, audio, subtitle, and export logic;
- `src/components/openai_client.py`: optional OpenAI integration;
- `test/`: offline test suite;
- `docs/architecture.md`: boundaries, limitations, and roadmap.

## Security and privacy

Review `SECURITY.md` before reporting a vulnerability. Video, audio, logs,
credentials, local environments, and generated output are intentionally ignored
by Git.

## License

See `LICENSE`.
