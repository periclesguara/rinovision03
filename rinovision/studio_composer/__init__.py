"""OBS-like composition foundation for RinoVision.

Importing this package never opens cameras, GUI windows, or media devices.
"""

from rinovision.studio_composer.controller import StudioComposerController, create_debug_scene, create_demo_layout, create_demo_multilayer
from rinovision.studio_composer.layout import create_empty_layout, lock_layout, unlock_layout
from rinovision.studio_composer.models import CanvasSpec, ComposerLayer, ComposerLayout, LayerSlot, LayerTransform, StudioComposerScene

__all__ = [
    "CanvasSpec",
    "ComposerLayout",
    "ComposerLayer",
    "LayerTransform",
    "LayerSlot",
    "StudioComposerScene",
    "StudioComposerController",
    "create_demo_layout",
    "create_demo_multilayer",
    "create_debug_scene",
    "create_empty_layout",
    "lock_layout",
    "unlock_layout",
]
