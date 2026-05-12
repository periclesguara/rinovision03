# RINOVISION03 Freeze

Audit date/time: 2026-05-11T21:06:52-03:00

## Environment

- Python: Python 3.10.12
- OS: Linux pop-os 6.16.3-76061603-generic x86_64
- Working directory: `/home/periclesguara/Projetos/RINOVISION03`
- File count excluding `.git` and `venv`: 264 at freeze start
- Git exists: yes
- `.env` exists: yes, contents not inspected or copied
- Tests exist: yes, legacy `test/` folder exists; modern `tests/` folder added after freeze

## Top-Level Folders At Freeze

- `.git`
- `__pycache__`
- `assets`
- `assistente`
- `components`
- `frames`
- `gui`
- `logs`
- `managers`
- `music`
- `output`
- `patch`
- `scripts`
- `src`
- `test`
- `utils`
- `venv`
- `windows`

## Safe Command Results

- `python --version`: passed.
- `python -m compileall .`: attempted with runtime/venv exclusions to avoid compiling third-party environment files. Failed because `assistente/crewai/AgenteCrewAI02/indexador/files_indexados/webcamcam_window_refactorv4.py` has invalid syntax at line 1.
- `pytest -q`: attempted. Failed because `pytest` was not installed in the active shell.
- `python main.py --help`: initially failed because `PySide6` was imported at module load. `main.py` was later adjusted so `--help` works before GUI imports.

Raw command outputs are saved in `docs/freeze_*.txt` files.
