# Architecture and limitations

## Boundaries

The desktop shell owns window lifecycle. Managers own scene, recording, audio,
subtitle, and export state. Hardware windows wrap camera and media playback. The
OpenAI client is optional and has no dependency on Qt.

## Data flow

1. `main.py` starts the Qt application and compositor.
2. Windows capture or display media.
3. `SceneManager` tracks logical objects and starts/stops the FFmpeg process.
4. Generated recordings and logs remain outside version control.
5. The optional text client sends an explicit user prompt through the Responses
   API and returns only `output_text`.

## Known limitations

- Recording currently assumes Linux, X11, and PulseAudio.
- Webcam/background processing requires local hardware and is not covered by CI.
- The application is a prototype; scene persistence and robust export recovery
  are not yet implemented.
- Qt tests run offscreen and validate construction, not physical devices.

## Roadmap

- isolate platform-specific capture backends;
- replace print statements with structured logging;
- add deterministic scene serialization;
- add fake-device integration tests;
- define explicit consent and retention controls for recordings.
