import importlib
import sys


def test_legacy_music_manager_import_has_no_runtime_side_effect(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    module = importlib.import_module("managers.editor_manager.music_manager")
    assert callable(module.inserir_musica_de_fundo)
    assert not (tmp_path / "music_manager.py").exists()


def test_music_adapter_imports_safely_without_moviepy(monkeypatch):
    monkeypatch.setitem(sys.modules, "moviepy", None)
    module = importlib.import_module("rinovision.editing.music")
    adapter = module.MusicAdapter()
    status = adapter.status()
    assert "available" in status


def test_healthcheck_reports_music_manager_capability():
    from scripts.rinovision_healthcheck import run_healthcheck

    report = run_healthcheck()
    capability = report["media_adapters"]["music_manager"]
    assert capability["import_ok"] is True
    assert capability["function_available"] is True
