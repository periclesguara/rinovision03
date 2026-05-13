import json
from pathlib import Path

from rinovision.studio_composer.models import ComposerLayer, ComposerLayout, StudioComposerScene, utc_now
from rinovision.studio_composer.storage import safe_path, studio_path, write_json
from rinovision.studio_composer.webcam_enhancement import default_webcam_enhancement


def create_empty_layout(project_id: str | None = None) -> ComposerLayout:
    scene = StudioComposerScene()
    if project_id:
        scene.project_id = project_id
    return scene


def create_scene(project_id: str | None = None) -> StudioComposerScene:
    return create_empty_layout(project_id)


def _next_z(scene: StudioComposerScene) -> int:
    return max((layer.z_index for layer in scene.layers), default=0) + 1


def add_layer(scene: StudioComposerScene, layer: ComposerLayer) -> ComposerLayer:
    if scene.locked:
        raise ValueError("scene is locked")
    existing_indexes = {item.z_index for item in scene.layers}
    if (layer.z_index <= 0 or layer.z_index in existing_indexes) and layer.layer_type != "empty":
        layer.z_index = _next_z(scene)
    scene.layers.append(layer)
    scene.selected_layer_id = layer.id
    scene.updated_at = utc_now()
    return layer


def get_layer(scene: StudioComposerScene, layer_id: str) -> ComposerLayer:
    for layer in scene.layers:
        if layer.id == layer_id:
            return layer
    raise KeyError(f"layer not found: {layer_id}")


def set_base_layer(scene: ComposerLayout, media_type: str, path: str | Path, width: float = 1280, height: float = 720) -> ComposerLayout:
    if scene.base_layer.locked or scene.locked:
        raise ValueError("base layer is locked")
    layer = ComposerLayer(name="Base", layer_type=media_type, source_path=str(path), width=width, height=height, z_index=0)
    scene.base_layer = layer
    scene.selected_layer_id = layer.id
    scene.updated_at = utc_now()
    return scene


def set_webcam_layer(
    scene: ComposerLayout,
    enabled: bool = True,
    camera_id: int = 0,
    mode: str = "free_floating",
    x: float = 900,
    y: float = 420,
    width: float = 320,
    height: float = 240,
) -> ComposerLayout:
    if scene.webcam_layer.locked or scene.locked:
        raise ValueError("webcam layer is locked")
    if mode not in {"inside_base", "free_floating"}:
        raise ValueError("webcam mode must be inside_base or free_floating")
    layer = scene.webcam_layer
    layer.enabled = enabled
    layer.camera_id = camera_id
    layer.mode = mode
    layer.metadata.setdefault("enhancement", default_webcam_enhancement())
    layer.x = x
    layer.y = y
    layer.width = width
    layer.height = height
    layer.metadata["frame_width"] = width
    layer.metadata["frame_height"] = height
    layer.metadata["stable_frame_size"] = True
    layer.z_index = max(layer.z_index, 99)
    scene.selected_layer_id = layer.id
    scene.updated_at = utc_now()
    return scene


def lock_layout(scene: ComposerLayout) -> ComposerLayout:
    scene.base_layer
    scene.webcam_layer
    scene.locked = True
    for layer in scene.layers:
        layer.locked = True
    scene.updated_at = utc_now()
    return scene


def unlock_layout(scene: ComposerLayout) -> ComposerLayout:
    scene.locked = False
    for layer in scene.layers:
        layer.locked = False
    scene.updated_at = utc_now()
    return scene


def save_layout(scene: ComposerLayout) -> Path:
    return write_json("layouts", f"{scene.project_id}_layout.json", scene.to_dict())


def load_layout(path: str | Path) -> StudioComposerScene:
    layouts_dir = studio_path("layouts")
    target = safe_path(layouts_dir, Path(path).name)
    return StudioComposerScene.from_dict(json.loads(target.read_text(encoding="utf-8")))
