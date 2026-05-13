import pytest

from rinovision.core.errors import PathSafetyError
from rinovision.studio_composer.media_loader import detect_media_type, import_media_file, import_multiple_media_files, validate_media_file
from rinovision.studio_composer.storage import get_studio_root


def _media_file(tmp_path, name):
    path = tmp_path / name
    path.write_bytes(b"placeholder")
    return path


def test_detect_media_type():
    assert detect_media_type("a.png") == "image"
    assert detect_media_type("a.mov") == "video"
    assert detect_media_type("a.txt") == "unsupported"


def test_unsupported_media_extension_is_rejected(tmp_path):
    path = _media_file(tmp_path, "bad.txt")
    with pytest.raises(ValueError):
        validate_media_file(path)


def test_path_traversal_is_rejected():
    with pytest.raises(PathSafetyError):
        validate_media_file("../escape.png")


def test_media_import_copies_into_studio_uploads(tmp_path):
    source = _media_file(tmp_path, "safe image.png")
    layer = import_media_file(source, "copy-test")
    root = get_studio_root()
    assert layer.source_path
    assert "studio_composer/uploads" in layer.source_path
    assert layer.layer_type == "image"
    assert layer.source_path.startswith(str(root))


def test_import_multiple_media_files(tmp_path):
    paths = [_media_file(tmp_path, "one.png"), _media_file(tmp_path, "two.mp4")]
    layers = import_multiple_media_files(paths, "multi-import")
    assert [layer.layer_type for layer in layers] == ["image", "video"]
    assert len({layer.id for layer in layers}) == 2
