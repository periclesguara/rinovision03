import pytest

from rinovision.core.errors import PathSafetyError
from rinovision.studio_composer.controller import create_demo_layout
from rinovision.studio_composer.storage import get_studio_root, studio_path, write_json


def test_storage_writes_only_under_studio_composer():
    root = get_studio_root()
    path = write_json("reports", "storage_test.json", {"ok": True})
    assert path.exists()
    assert path.resolve().is_relative_to(root.resolve())


def test_storage_rejects_path_traversal():
    with pytest.raises(PathSafetyError):
        studio_path("layouts", "../escape.json")


def test_demo_layout_writes_locked_layout():
    result = create_demo_layout("studio-demo-test")
    assert result["layout"]["base_layer"]["locked"] is True
    assert result["layout"]["webcam_layer"]["locked"] is True
    assert result["layout_path"].endswith("studio-demo-test_layout.json")
