# RinoVision Studio Composer

## Concept

Studio Composer is the pre-recording stage for RinoVision. It behaves like a simplified OBS/Canva scene editor: the user prepares a canvas, uploads multiple images and videos, places the computer webcam preview as an independent overlay, adjusts order and transforms, then locks the final scene.

Recording is intentionally not part of this module yet.

## Architecture

- `models.py`: JSON-serializable canvas, layer, and scene dataclasses.
- `storage.py`: safe storage under `data/studio_composer/`.
- `layout.py`: create, update, lock, unlock, save, and load scenes.
- `media_loader.py`: supported upload validation and copying into Studio Composer storage.
- `video_preview.py`: first-frame preview helper, with ffmpeg as optional runtime dependency.
- `video_playback.py`: selected-layer play/pause preview helper, with lazy OpenCV use.
- `webcam_enhancement.py`: real-time webcam brightness, contrast, saturation, gamma placeholder, and mirror helpers.
- `webcam_overlay.py`: wrapper around `WebcamPreviewController`; no camera opens during import.
- `controller.py`: headless orchestration, layer operations, z-order, and demo scene creation.
- `ui/`: optional PySide6 QGraphicsView screen.

## OBS-Style Layer Slots

The composer uses numbered slots like a simplified OBS stack:

- Layer 1 is foreground and renders above all other slots.
- Layer 2 is the second plane and renders behind Layer 1.
- Layer 3 is an optional background and renders behind Layer 2.
- Layer 4 is an optional deeper background and renders behind Layer 3.

Webcam, image, video, and future text/annotation sources can be assigned to any layer slot. Empty slots are valid. Multiple sources per slot are allowed; `local_z_index` controls order inside that slot.

Layer slots are not spatial quadrants. They do not constrain a source to a region of the canvas. Slot choice controls visual stacking only; `x` and `y` control position on the canvas.

Examples:

- Commentary over video: Layer 1 webcam, Layer 2 video.
- Commentary over image: Layer 1 webcam, Layer 2 image, Layer 3 background.
- Rich composition: Layer 1 logo, Layer 2 webcam, Layer 3 main video, Layer 4 background.

## Layer Model

The scene contains:

- four OBS-style layer slots
- optional primary base layer
- multiple image/video sources
- one webcam source
- future text/annotation layers

Each layer stores:

- `id`
- `name`
- `layer_type`
- `layer_slot`
- `source_path`
- transform values: `x`, `y`, `width`, `height`, `scale`, `rotation`
- `opacity`
- `local_z_index`
- `computed_z_index`
- `locked`
- `visible`
- `metadata`

## Layout JSON

Layouts are saved under `data/studio_composer/layouts/`:

```json
{
  "project_id": "...",
  "canvas": {
    "width": 1280,
    "height": 720,
    "aspect_ratio": "16:9",
    "background_color": "#000000"
  },
  "layer_slots": [
    {
      "slot_number": 1,
      "name": "Layer 1",
      "description": "Foreground / first plane",
      "z_base": 4000,
      "enabled": true
    }
  ],
  "layers": [
    {
      "id": "...",
      "name": "Image 1",
      "layer_type": "image",
      "layer_slot": 2,
      "source_path": "...",
      "x": 100,
      "y": 80,
      "width": 640,
      "height": 360,
      "scale": 1.0,
      "rotation": 0.0,
      "opacity": 1.0,
      "local_z_index": 0,
      "computed_z_index": 3000,
      "locked": false,
      "visible": true,
      "metadata": {}
    }
  ],
  "selected_layer_id": "...",
  "locked": false
}
```

## Commands

Headless layout demos:

```bash
python main.py --studio-composer-demo-layout
python main.py --studio-composer-demo-multilayer
```

Manual GUI:

```bash
python main.py --studio-composer
```

## Current UI Behavior

- Upload Image supports repeated uploads and multi-select.
- Upload Video supports repeated uploads and multi-select.
- Image layer, video layer, and webcam layer controls assign new sources to Layer 1, 2, 3, or 4.
- Selected Layer control moves the selected source to a new slot and recomputes visual stacking immediately.
- Slot changes update the selected `QGraphicsItem` z-order and preserve the source `x`/`y` position.
- Video layers use first-frame preview on upload.
- `Play/Pause` starts or pauses the selected video layer with a controlled QTimer.
- Layers are selectable and draggable.
- Selected image and video layers show direct corner resize handles on the canvas.
- Direct resize updates `width` and `height` in the model, inspector, and saved layout.
- `Scale +` and `Scale -` resize the selected image, video, or webcam layer.
- Webcam image controls adjust brightness, contrast, saturation, mirror mode, and reset for the selected webcam layer.
- Forward/Backward changes selected layer `local_z_index` within its current slot.
- Lock freezes all current layers and saves the scene.
- Unlock allows editing again.
- Reset Layer resets only the selected layer transform.

Lock blocks movement, direct resize, and layer slot changes. Unlock restores editability.

## Webcam Enhancement

The webcam layer stores enhancement settings in layer metadata:

```json
{
  "enhancement": {
    "brightness": 0,
    "contrast": 1.0,
    "saturation": 1.0,
    "gamma": 1.0,
    "mirror": true
  }
}
```

These adjustments are applied only while the webcam preview is active. They are software-based and cannot fully compensate for poor lighting.

Recommended setup:

- soft front light
- avoid backlight
- camera at eye level
- clean background
- avoid strong shadows

## Future Record Step

The future recorder should consume only locked scenes. Raw webcam and media layers should be composed from saved transform metadata, then passed into the existing editing/export pipeline. The Studio Composer remains a preparation screen, not a recorder.
