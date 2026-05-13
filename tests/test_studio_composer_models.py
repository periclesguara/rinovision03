from rinovision.studio_composer import ComposerLayout, create_empty_layout


def test_studio_composer_imports_without_opening_webcam():
    layout = create_empty_layout()
    assert isinstance(layout, ComposerLayout)
    assert layout.base_layer.type == "empty"
    assert layout.webcam_layer.enabled is False


def test_layout_json_can_be_created():
    layout = create_empty_layout("project-123")
    payload = layout.to_dict()
    assert payload["project_id"] == "project-123"
    assert payload["canvas"]["width"] == 1280
    assert payload["canvas"]["height"] == 720
