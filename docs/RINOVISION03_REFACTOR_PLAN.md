# RINOVISION03 Refactor Plan

## Principle

Preserve working legacy code and add a professional foundation beside it. Do not mass move or delete files until imports, tests, and compatibility wrappers prove the move is safe.

## Phase 1: Stabilize

- Keep `main.py` as the legacy GUI entry point.
- Keep `windows/`, `components/`, `managers/`, and `utils/` intact.
- Route all new runtime artifacts to `data/`.
- Keep `.env` ignored and use `.env.example` only for placeholders.

## Phase 2: Core Package

- Use `rinovision.paths` for data safety.
- Use `rinovision.core.project` and `rinovision.core.artifact_registry` for project manifests.
- Use `rinovision.core.pipeline` for explicit status transitions.

## Phase 3: Product Pipelines

- Build AI Video Maker as raw-media generation, never as final export.
- Route AI raw video into editing.
- Build editing as source probe, edit plan, render/placeholder, and export package.

## Phase 4: Legacy Wrapping

- Wrap importable managers through `rinovision.capture` and `rinovision.editing`.
- Keep failed imports as documented stubs instead of crashing.
- Create GUI compatibility adapters before renaming windows.

## Phase 5: Archive Later

- Only move files into `legacy/` when no imports reference them, compile/tests pass, and a reversible note is written.

## Current Working Commands

- `python scripts/rinovision_healthcheck.py`
- `python -m compileall rinovision scripts tests`
- `pytest -q`
- `python main.py --healthcheck`
- `python main.py --safe-mode`
- `python main.py --ai-video-demo`
- `python main.py --editing-demo`

## Next Refactor Targets

- Replace import-time side effects in legacy assistant and music manager scripts.
- Normalize `managers/editor_manager` imports so UI files do not import stale module paths.
- Decide the canonical webcam manager/window after hardware validation.
- Move duplicated indexed files to `legacy/` only after references are checked.
