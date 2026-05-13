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
- `webcam_overlay.py`: wrapper around `WebcamPreviewController`; no camera opens during import.
- `controller.py`: headless orchestration, layer operations, z-order, and demo scene creation.
- `ui/`: optional PySide6 QGraphicsView screen.

## Layer Model

The scene contains:

- optional primary base layer
- multiple image layers
- multiple video layers
- one webcam layer
- future text/annotation layers

Each layer stores:

- `id`
- `name`
- `layer_type`
- `source_path`
- transform values: `x`, `y`, `width`, `height`, `scale`, `rotation`
- `opacity`
- `z_index`
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
  "layers": [
    {
      "id": "...",
      "name": "Image 1",
      "layer_type": "image",
      "source_path": "...",
      "x": 100,
      "y": 80,
      "width": 640,
      "height": 360,
      "scale": 1.0,
      "rotation": 0.0,
      "opacity": 1.0,
      "z_index": 1,
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
- Video layers use first-frame preview on upload.
- `Play/Pause` starts or pauses the selected video layer with a controlled QTimer.
- Layers are selectable and draggable.
- `Scale +` and `Scale -` resize the selected image, video, or webcam layer.
- Forward/Backward changes selected layer `z_index`.
- Lock freezes all current layers and saves the scene.
- Unlock allows editing again.
- Reset Layer resets only the selected layer transform.

## Future Record Step

The future recorder should consume only locked scenes. Raw webcam and media layers should be composed from saved transform metadata, then passed into the existing editing/export pipeline. The Studio Composer remains a preparation screen, not a recorder.
