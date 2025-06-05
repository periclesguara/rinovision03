def auto_patch(window):
    try:
        from patch.patch_compositor import apply_patch_to_compositor
        apply_patch_to_compositor(window)
    except Exception as e:
        print(f"[PATCH] Erro ao aplicar patch: {e}")
