# RinoVision Studio Composer GUI Fix

## Audit

The Studio Composer backend already supported OBS-style layer slots through `layer_slot`, `local_z_index`, and `computed_z_index`, but the GUI wiring was incomplete.

Findings:

- Upload controls used one generic media slot selector for both images and videos.
- Webcam had a slot selector, but selected-layer slot changes required a separate button.
- Selecting a canvas item updated the inspector, but the selected slot control did not act as a live editor.
- Changing a layer slot in the model could recompute `computed_z_index`, but the UI path was not consistently applying `QGraphicsItem.setZValue()`.
- Image/video layer movement was wired through `movement_callback`.
- Direct resize handles were missing from canvas items; only `Scale +` and `Scale -` existed.
- Lock blocked controller edits, but the GUI needed to block slot changes and direct resize as visible interactions.

## Fix

Implemented GUI wiring so layer slots are real visual depth controls:

- Added explicit UI controls for image layer slot, video layer slot, webcam layer slot, and selected layer slot.
- Image uploads read the image layer slot selector.
- Video uploads read the video layer slot selector.
- Webcam overlay reads the webcam layer slot selector.
- Changing the selected layer slot now immediately calls `move_layer_to_slot()`.
- The selected item keeps the same `x` and `y` position when its slot changes.
- The selected item updates `computed_z_index`.
- The selected `QGraphicsItem` updates `setZValue()` to reflect the new depth.
- The layer panel refreshes after slot changes.
- The inspector refreshes after selection, movement, resize, slot change, and lock/unlock.

## Direct Resize

Canvas items now share direct resize behavior:

- selected image/video placeholder and pixmap items show visible corner resize handles;
- dragging a corner resizes the visual item;
- resize updates `layer.width` and `layer.height`;
- resize persists through layout JSON when saved;
- locked layers cannot resize;
- globally locked scenes cannot resize;
- existing `Scale +` and `Scale -` behavior remains available.

## OBS Slot Semantics

Layer slots are depth slots only:

- Layer 1 is foreground/top.
- Layer 2 is behind Layer 1.
- Layer 3 is behind Layer 2.
- Layer 4 is deepest background.

Slot changes do not move an item on the canvas. Position is still controlled by `x` and `y`.

## Debug Command

Headless diagnostic command:

```bash
python main.py --studio-composer-debug-scene
```

It creates a scene with Layer 1 webcam, Layer 2 video, Layer 3 image, Layer 4 empty, saves layout JSON, prints layer positions and computed z-order, and verifies `Layer 1 > Layer 2 > Layer 3`.

## Manual GUI Checklist

```bash
python main.py --studio-composer
```

- Add video to Layer 2.
- Add webcam to Layer 1.
- Confirm webcam appears above video.
- Add image to Layer 3.
- Confirm image appears behind video.
- Select video and move it to Layer 1.
- Confirm it comes forward without x/y jump.
- Resize image directly by a corner handle.
- Resize video directly by a corner handle.
- Lock scene and confirm movement, resize, and slot changes are blocked.
- Unlock scene and confirm editing returns.
