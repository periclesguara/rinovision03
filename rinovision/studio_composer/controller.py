from pathlib import Path

from rinovision.studio_composer.layout import (
    add_layer,
    create_scene,
    get_layer,
    load_layout as load_layout_file,
    lock_layout,
    save_layout as save_scene_layout,
    set_webcam_layer,
    unlock_layout,
)
from rinovision.studio_composer.media_loader import import_media_file, import_multiple_media_files
from rinovision.studio_composer.models import (
    ComposerLayer,
    StudioComposerScene,
    compute_z_index,
    create_default_layer_slots,
    utc_now,
    validate_layer_slot,
)


class StudioComposerController:
    def __init__(self, project_id: str | None = None):
        self.scene = create_scene(project_id)

    @property
    def layout(self) -> StudioComposerScene:
        return self.scene

    @layout.setter
    def layout(self, value: StudioComposerScene):
        self.scene = value

    def create_default_layer_slots(self):
        self.scene.layer_slots = create_default_layer_slots()
        return self.scene.layer_slots

    def validate_layer_slot(self, slot_number: int) -> int:
        return validate_layer_slot(slot_number)

    def compute_z_index(self, layer_slot: int, local_z_index: int = 0) -> int:
        return compute_z_index(layer_slot, local_z_index)

    def add_image_layer(self, path: str | Path, layer_slot: int = 2) -> ComposerLayer:
        layer = import_media_file(path, self.scene.project_id, layer_slot=layer_slot)
        if layer.layer_type != "image":
            raise ValueError("selected media is not an image")
        return add_layer(self.scene, layer)

    def add_video_layer(self, path: str | Path, layer_slot: int = 2) -> ComposerLayer:
        layer = import_media_file(path, self.scene.project_id, layer_slot=layer_slot)
        if layer.layer_type != "video":
            raise ValueError("selected media is not a video")
        return add_layer(self.scene, layer)

    def add_media_layers(self, paths: list[str | Path], layer_slot: int = 2) -> list[ComposerLayer]:
        layers = import_multiple_media_files(paths, self.scene.project_id, layer_slot=layer_slot)
        return [add_layer(self.scene, layer) for layer in layers]

    def import_base(self, source_path: str | Path) -> dict:
        layer = import_media_file(source_path, self.scene.project_id, layer_slot=2)
        layer.name = "Primary Base"
        layer.local_z_index = 0
        layer.recompute_z_index()
        add_layer(self.scene, layer)
        return {"type": layer.layer_type, "path": layer.source_path, "layer_id": layer.id}

    def enable_webcam_overlay(self, camera_id: int = 0, mode: str = "free_floating", layer_slot: int = 1) -> StudioComposerScene:
        return set_webcam_layer(self.scene, enabled=True, camera_id=camera_id, mode=mode, layer_slot=layer_slot)

    def add_webcam_layer(self, enabled: bool = False, camera_id: int = 0, mode: str = "free_floating", layer_slot: int = 1) -> ComposerLayer:
        set_webcam_layer(self.scene, enabled=enabled, camera_id=camera_id, mode=mode, layer_slot=layer_slot)
        return self.scene.webcam_layer

    def select_layer(self, layer_id: str) -> ComposerLayer:
        layer = get_layer(self.scene, layer_id)
        self.scene.selected_layer_id = layer.id
        self.scene.updated_at = utc_now()
        return layer

    def move_layer(self, layer_id: str, x: float, y: float) -> ComposerLayer:
        layer = get_layer(self.scene, layer_id)
        self._ensure_editable(layer)
        layer.x = x
        layer.y = y
        layer.metadata["updated_at"] = utc_now()
        self.scene.updated_at = utc_now()
        return layer

    def resize_layer(self, layer_id: str, width: float, height: float) -> ComposerLayer:
        layer = get_layer(self.scene, layer_id)
        self._ensure_editable(layer)
        layer.width = width
        layer.height = height
        layer.metadata["updated_at"] = utc_now()
        self.scene.updated_at = utc_now()
        return layer

    def scale_layer(self, layer_id: str, scale: float) -> ComposerLayer:
        layer = get_layer(self.scene, layer_id)
        self._ensure_editable(layer)
        layer.scale = scale
        layer.metadata["updated_at"] = utc_now()
        self.scene.updated_at = utc_now()
        return layer

    def set_layer_z_index(self, layer_id: str, z_index: int) -> ComposerLayer:
        layer = get_layer(self.scene, layer_id)
        self._ensure_editable(layer)
        layer.local_z_index = int(z_index)
        layer.recompute_z_index()
        self.scene.updated_at = utc_now()
        return layer

    def move_layer_to_slot(self, layer_id: str, layer_slot: int) -> ComposerLayer:
        layer = get_layer(self.scene, layer_id)
        self._ensure_editable(layer)
        layer.layer_slot = validate_layer_slot(layer_slot)
        layer.recompute_z_index()
        layer.metadata["updated_at"] = utc_now()
        self.scene.updated_at = utc_now()
        return layer

    def get_layers_by_slot(self, slot_number: int) -> list[ComposerLayer]:
        slot_number = validate_layer_slot(slot_number)
        return sorted([layer for layer in self.scene.layers if layer.layer_slot == slot_number], key=lambda item: item.local_z_index, reverse=True)

    def get_scene_layers_grouped_by_slot(self) -> dict[int, list[ComposerLayer]]:
        return {slot.slot_number: self.get_layers_by_slot(slot.slot_number) for slot in self.scene.layer_slots}

    def bring_forward_within_slot(self, layer_id: str) -> ComposerLayer:
        layer = get_layer(self.scene, layer_id)
        self._ensure_editable(layer)
        slot_layers = self.get_layers_by_slot(layer.layer_slot)
        layer.local_z_index = max((item.local_z_index for item in slot_layers), default=-1) + 1
        layer.recompute_z_index()
        self.scene.updated_at = utc_now()
        return layer

    def send_backward_within_slot(self, layer_id: str) -> ComposerLayer:
        layer = get_layer(self.scene, layer_id)
        self._ensure_editable(layer)
        slot_layers = self.get_layers_by_slot(layer.layer_slot)
        layer.local_z_index = min((item.local_z_index for item in slot_layers), default=1) - 1
        layer.recompute_z_index()
        self.scene.updated_at = utc_now()
        return layer

    def bring_forward(self, layer_id: str) -> ComposerLayer:
        return self.bring_forward_within_slot(layer_id)

    def send_backward(self, layer_id: str) -> ComposerLayer:
        return self.send_backward_within_slot(layer_id)

    def toggle_layer_visibility(self, layer_id: str) -> ComposerLayer:
        layer = get_layer(self.scene, layer_id)
        self._ensure_editable(layer)
        layer.visible = not layer.visible
        if layer.layer_type == "webcam":
            layer.metadata["enabled"] = layer.visible
        self.scene.updated_at = utc_now()
        return layer

    def lock_layer(self, layer_id: str) -> ComposerLayer:
        layer = get_layer(self.scene, layer_id)
        layer.locked = True
        self.scene.updated_at = utc_now()
        return layer

    def unlock_layer(self, layer_id: str) -> ComposerLayer:
        if self.scene.locked:
            raise ValueError("scene is locked")
        layer = get_layer(self.scene, layer_id)
        layer.locked = False
        self.scene.updated_at = utc_now()
        return layer

    def lock_scene(self) -> Path:
        lock_layout(self.scene)
        return save_scene_layout(self.scene)

    def unlock_scene(self) -> StudioComposerScene:
        return unlock_layout(self.scene)

    def lock(self) -> Path:
        return self.lock_scene()

    def unlock(self) -> StudioComposerScene:
        return self.unlock_scene()

    def reset(self) -> StudioComposerScene:
        self.scene = create_scene(self.scene.project_id)
        return self.scene

    def save_layout(self) -> Path:
        return save_scene_layout(self.scene)

    def save(self) -> Path:
        return self.save_layout()

    def load_layout(self, path: str | Path) -> StudioComposerScene:
        self.scene = load_layout_file(path)
        return self.scene

    def _ensure_editable(self, layer: ComposerLayer):
        if self.scene.locked or layer.locked:
            raise ValueError("layer is locked")


def create_demo_layout(project_id: str | None = None) -> dict:
    controller = StudioComposerController(project_id)
    controller.enable_webcam_overlay(camera_id=0, mode="free_floating", layer_slot=1)
    layout_path = controller.lock_scene()
    return {
        "project_id": controller.scene.project_id,
        "layout_path": str(layout_path),
        "layout": controller.scene.to_dict(),
    }


def create_demo_multilayer(project_id: str | None = None) -> dict:
    controller = StudioComposerController(project_id)
    video = ComposerLayer(
        name="Fake Video Layer 2",
        layer_type="video",
        layer_slot=2,
        source_path="data/studio_composer/uploads/fake_video.mp4",
        x=0,
        y=0,
        width=1280,
        height=720,
        local_z_index=0,
        metadata={"preview_mode": "playback"},
    )
    image = ComposerLayer(
        name="Fake Background Layer 3",
        layer_type="image",
        layer_slot=3,
        source_path="data/studio_composer/uploads/fake_background.png",
        x=0,
        y=0,
        width=1280,
        height=720,
        local_z_index=0,
        metadata={"adjustments": {"brightness": 0, "contrast": 0, "crop": None, "fit_mode": "contain"}},
    )
    add_layer(controller.scene, video)
    add_layer(controller.scene, image)
    controller.add_webcam_layer(enabled=False, camera_id=0, mode="free_floating", layer_slot=1)
    layout_path = controller.lock_scene()
    active_slots = sorted({layer.layer_slot for layer in controller.scene.layers if layer.visible or layer.layer_type == "webcam"})
    return {
        "project_id": controller.scene.project_id,
        "layout_path": str(layout_path),
        "layer_count": len(controller.scene.layers),
        "active_slots": active_slots,
        "layout": controller.scene.to_dict(),
    }
