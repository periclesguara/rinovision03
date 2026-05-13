from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


LAYER_TYPES = {"image", "video", "webcam", "empty", "text_future"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Canvas:
    width: int = 1280
    height: int = 720
    aspect_ratio: str = "16:9"
    background_color: str = "#000000"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


CanvasSpec = Canvas


@dataclass
class ComposerLayer:
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = "Layer"
    layer_type: str = "empty"
    source_path: str | None = None
    x: float = 0
    y: float = 0
    width: float = 1280
    height: float = 720
    scale: float = 1.0
    rotation: float = 0.0
    opacity: float = 1.0
    z_index: int = 0
    locked: bool = False
    visible: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.layer_type not in LAYER_TYPES:
            raise ValueError(f"unsupported layer type: {self.layer_type}")

    @property
    def type(self) -> str:
        return self.layer_type

    @type.setter
    def type(self, value: str):
        if value not in LAYER_TYPES:
            raise ValueError(f"unsupported layer type: {value}")
        self.layer_type = value

    @property
    def path(self) -> str:
        return self.source_path or ""

    @path.setter
    def path(self, value: str | None):
        self.source_path = value or None

    @property
    def enabled(self) -> bool:
        return bool(self.metadata.get("enabled", self.visible))

    @enabled.setter
    def enabled(self, value: bool):
        self.metadata["enabled"] = bool(value)
        self.visible = bool(value)

    @property
    def camera_id(self) -> int:
        return int(self.metadata.get("camera_id", 0))

    @camera_id.setter
    def camera_id(self, value: int):
        self.metadata["camera_id"] = int(value)

    @property
    def mode(self) -> str:
        return str(self.metadata.get("mode", "free_floating"))

    @mode.setter
    def mode(self, value: str):
        if value not in {"inside_base", "free_floating"}:
            raise ValueError("webcam mode must be inside_base or free_floating")
        self.metadata["mode"] = value

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ComposerLayer":
        normalized = dict(data)
        if "type" in normalized and "layer_type" not in normalized:
            normalized["layer_type"] = normalized.pop("type")
        if "path" in normalized and "source_path" not in normalized:
            normalized["source_path"] = normalized.pop("path")
        return cls(**normalized)


LayerTransform = ComposerLayer
WebcamLayer = ComposerLayer


@dataclass
class StudioComposerScene:
    project_id: str = field(default_factory=lambda: str(uuid4()))
    canvas: Canvas = field(default_factory=Canvas)
    layers: list[ComposerLayer] = field(default_factory=list)
    selected_layer_id: str | None = None
    locked: bool = False
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    @property
    def base_layer(self) -> ComposerLayer:
        for layer in self.layers:
            if layer.layer_type in {"image", "video", "empty"}:
                return layer
        layer = ComposerLayer(name="Empty Base", layer_type="empty", z_index=0, locked=self.locked)
        self.layers.insert(0, layer)
        self.selected_layer_id = self.selected_layer_id or layer.id
        return layer

    @base_layer.setter
    def base_layer(self, value: ComposerLayer):
        for index, layer in enumerate(self.layers):
            if layer.layer_type in {"image", "video", "empty"}:
                self.layers[index] = value
                return
        self.layers.insert(0, value)

    @property
    def webcam_layer(self) -> ComposerLayer:
        for layer in self.layers:
            if layer.layer_type == "webcam":
                return layer
        layer = ComposerLayer(
            name="Webcam",
            layer_type="webcam",
            source_path=None,
            x=900,
            y=420,
            width=320,
            height=240,
            z_index=99,
            visible=False,
            metadata={"camera_id": 0, "mode": "free_floating", "enabled": False},
        )
        self.layers.append(layer)
        return layer

    @webcam_layer.setter
    def webcam_layer(self, value: ComposerLayer):
        for index, layer in enumerate(self.layers):
            if layer.layer_type == "webcam":
                self.layers[index] = value
                return
        self.layers.append(value)

    def selected_layer(self) -> ComposerLayer | None:
        if self.selected_layer_id is None:
            return None
        return next((layer for layer in self.layers if layer.id == self.selected_layer_id), None)

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "canvas": self.canvas.to_dict(),
            "layers": [layer.to_dict() for layer in sorted(self.layers, key=lambda item: item.z_index)],
            "base_layer": self.base_layer.to_dict(),
            "webcam_layer": self.webcam_layer.to_dict(),
            "selected_layer_id": self.selected_layer_id,
            "locked": self.locked,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StudioComposerScene":
        if "layers" in data:
            layers = [ComposerLayer.from_dict(item) for item in data.get("layers", [])]
        else:
            layers = []
            base = data.get("base_layer")
            webcam = data.get("webcam_layer")
            if base:
                layers.append(ComposerLayer.from_dict(base))
            if webcam:
                webcam_data = dict(webcam)
                webcam_data.setdefault("layer_type", "webcam")
                webcam_data.setdefault("name", "Webcam")
                webcam_data.setdefault("source_path", None)
                webcam_data.setdefault(
                    "metadata",
                    {
                        "camera_id": webcam_data.pop("camera_id", 0),
                        "mode": webcam_data.pop("mode", "free_floating"),
                        "enabled": webcam_data.pop("enabled", False),
                    },
                )
                layers.append(ComposerLayer.from_dict(webcam_data))
        return cls(
            project_id=data["project_id"],
            canvas=Canvas(**data.get("canvas", {})),
            layers=layers,
            selected_layer_id=data.get("selected_layer_id"),
            locked=bool(data.get("locked", False)),
            created_at=data.get("created_at", utc_now()),
            updated_at=data.get("updated_at", utc_now()),
        )


ComposerLayout = StudioComposerScene
