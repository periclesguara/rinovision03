# RINOVISION03 Legacy Candidates

No files were moved to `legacy/` in this pass.

## Candidate Files/Folders

- `managers/webcam_manager_refactorv1.py`
- `windows/webcam_window_refactor.py`
- `windows/webcam_window_refactor_v2.py`
- `windows/webcam_window_refactorv3.py`
- `windows/webcam_window_refactorv4.py`
- duplicated `assistente/AgenteCrewAI02/` and `assistente/crewai/AgenteCrewAI02/`
- `patch/patch_compositor.py` if replaced by official compositor behavior
- `scripts/patch_*.sh` if no longer needed
- indexed copies under `assistente/crewai/AgenteCrewAI02/indexador/files_indexados/`

## Move Criteria

Move only after:

- no active imports reference the file;
- compile/tests still pass;
- compatibility wrappers exist where needed;
- the move is documented and reversible.
