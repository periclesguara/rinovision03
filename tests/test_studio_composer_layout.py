from rinovision.studio_composer.layout import create_empty_layout, lock_layout, set_webcam_layer, unlock_layout


def test_layout_lock_marks_layers_locked():
    layout = create_empty_layout()
    set_webcam_layer(layout, enabled=True, mode="inside_base")
    lock_layout(layout)
    assert layout.base_layer.locked is True
    assert layout.webcam_layer.locked is True


def test_unlock_allows_editing():
    layout = create_empty_layout()
    lock_layout(layout)
    unlock_layout(layout)
    assert layout.base_layer.locked is False
    assert layout.webcam_layer.locked is False
    set_webcam_layer(layout, enabled=True, mode="free_floating", x=10)
    assert layout.webcam_layer.x == 10


def test_invalid_webcam_mode_fails():
    layout = create_empty_layout()
    try:
        set_webcam_layer(layout, mode="outside")
    except ValueError as exc:
        assert "inside_base" in str(exc)
    else:
        raise AssertionError("invalid webcam mode should fail")
