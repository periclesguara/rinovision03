# RinoVision Studio Composer Layer Slot GUI Fix

## Diagnosis

The OBS-style layer slot model was present, but the real GUI needed a stricter wiring path from the dropdown controls to the canvas `QGraphicsItem`.

Current controls:

- `image_layer_slot_combo` controls the slot for newly uploaded images.
- `video_layer_slot_combo` controls the slot for newly uploaded videos.
- `webcam_layer_slot_combo` controls the slot for the webcam layer.
- `selected_layer_slot_combo` controls the slot of the currently selected source.

Checks performed:

- Image upload reads `image_layer_slot_combo`.
- Video upload reads `video_layer_slot_combo`.
- Webcam layer creation reads `webcam_layer_slot_combo`.
- Selected source slot changes call `controller.move_layer_to_slot(...)`.
- Slot changes recompute `computed_z_index`.
- The matching canvas item is retrieved by `layer_id`.
- The item calls `QGraphicsItem.setZValue(layer.computed_z_index)`.
- Inspector and layer panel refresh after slot changes.

## Disconnects Fixed

- Upload paths now use explicit helper methods:
  - `add_image_path_to_selected_slot(path)`
  - `add_video_path_to_selected_slot(path)`
  - `add_webcam_layer_to_selected_slot(...)`
- Source-specific combo choices are read at creation time. Defaults apply only if the user has not changed the combo.
- `StudioCanvasView` now exposes explicit layer-item mapping helpers:
  - `get_item_by_layer_id(layer_id)`
  - `update_item_z_value(layer_id, z_value)`
  - `sync_item_z_order(layer)`
  - `refresh_all_z_values_from_model(layers)`
  - `refresh_layer_order(layers)`
  - `sync_item_from_layer(layer)`
  - `select_layer_item(layer_id)`
- Newly created media is selected immediately, so the inspector shows the real layer slot.
- The selected-layer slot dropdown updates the model and the actual canvas item z-order.
- Locked scenes and locked layers block slot changes and revert the dropdown to the current slot.
- Regression coverage now verifies the exact reported case: Webcam in Layer 2 and Image in Layer 1 results in the image model and graphics item above the webcam.

## Debug Logging

Set this environment variable before launching the GUI to print source assignment details:

```bash
RINOVISION_STUDIO_DEBUG=1 python main.py --studio-composer
```

Each added source prints the selected slot, final model slot, `computed_z_index`, and current `QGraphicsItem.zValue()`.

## Slot Semantics

Layer slots are depth/z-order only:

- Layer 1 is foreground/top.
- Layer 2 is behind Layer 1.
- Layer 3 is behind Layer 2.
- Layer 4 is deepest background.

Changing a layer slot does not change `x`, `y`, `width`, or `height`.

## Manual Validation

Run:

```bash
python main.py --studio-composer
```

Checklist:

- Add video to Layer 2.
- Add webcam to Layer 1.
- Confirm webcam appears above video.
- Add image to Layer 3.
- Confirm image appears behind video.
- Select video.
- Change video from Layer 2 to Layer 1.
- Confirm video comes forward.
- Confirm video `x`/`y` did not jump.
- Select image.
- Change image from Layer 3 to Layer 1.
- Confirm image comes forward.
- Confirm image `x`/`y` did not jump.
- Select webcam.
- Change webcam from Layer 1 to Layer 2.
- Confirm webcam moves behind Layer 1 items.
- Lock scene.
- Try changing selected layer slot and confirm change is blocked.
- Unlock scene and confirm layer slot changes work again.
