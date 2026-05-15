# RinoVision Studio Composer GUI Repaint Fix

## Audit

The repaint artifact appeared during layer movement and direct resize in the PySide6 `QGraphicsView` Studio Composer canvas.

Findings:

- `StudioCanvasView` was using the default `QGraphicsView` viewport update mode.
- The scene and view had a dark background brush, but the viewport itself was not explicitly configured for conservative repaint.
- Custom layer items override `paint()` to draw resize handles.
- Resize handles were drawn around the media rectangle, partly outside the default Qt item `boundingRect()`.
- The item `boundingRect()` did not include handle padding, so Qt could repaint too small an area.
- Resize changed pixmap/rect dimensions without an explicit `prepareGeometryChange()` call in the shared resize path.
- Movable/resizable items did not explicitly disable item cache.
- Movement already synced `x` and `y` through the controller, but view/scene repaint was not explicitly requested after every movement/selection/resize path.

## Fix Applied

The fix favors correctness over repaint performance.

In `StudioCanvasView`:

- Uses `QGraphicsView.ViewportUpdateMode.FullViewportUpdate`.
- Disables view cache with `QGraphicsView.CacheModeFlag.CacheNone`.
- Keeps painter state optimization conservative.
- Sets the scene background brush and viewport palette to the same stable dark background.
- Adds `request_repaint()` to update the scene and viewport after visual changes.

In `layer_items.py`:

- Movable/resizable items disable item cache with `NoCache`.
- Custom `boundingRect()` now includes padding for selection borders and resize handles.
- Resize handles are calculated from the media content rectangle, not from the padded bounding rectangle.
- `prepareGeometryChange()` is called before width/height changes.
- Item and scene updates are requested after movement, resize, selection changes, and lock/unlock state changes.

In `studio_window.py`:

- Selection, movement, resize, z-order changes, lock/unlock, scale, and reset paths request canvas repaint.

## Manual Validation

Run:

```bash
python main.py --studio-composer
```

Checklist:

- Upload image to Layer 2.
- Drag image around canvas for 10 seconds.
- Confirm no ghost trails or dotted marks remain.
- Resize image from corners.
- Confirm no stale outlines remain.
- Upload video to Layer 2.
- Play video.
- Drag video while paused.
- Confirm no marks remain.
- Drag video after play/pause.
- Confirm no marks remain.
- Enable webcam in Layer 1.
- Move webcam overlay.
- Confirm no marks remain.
- Lock scene and confirm movement is blocked.
- Unlock scene and confirm movement works without visual residue.

## Notes

Automated tests verify repaint-safe configuration, padded bounding rectangles, no-cache item mode, resize path, movement path, and selection toggling in Qt offscreen mode. Visual artifact absence still requires manual GUI validation because it depends on the local graphics stack.
