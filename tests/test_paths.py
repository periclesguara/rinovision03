import pytest

from rinovision.paths import ensure_data_dirs, get_data_root, safe_path


def test_safe_path_rejects_traversal():
    base = get_data_root()
    with pytest.raises(ValueError):
        safe_path(base, "..", "outside.txt")


def test_data_dirs_are_created():
    root = ensure_data_dirs()
    assert root.exists()
    assert (root / "input").exists()
    assert (root / "ai_video" / "prompts").exists()
