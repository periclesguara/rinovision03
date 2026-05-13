def adjustment_placeholders() -> dict:
    return {
        "brightness": {"implemented": False, "message": "Brightness adjustment is reserved for the next image pipeline step."},
        "contrast": {"implemented": False, "message": "Contrast adjustment is reserved for the next image pipeline step."},
        "crop": {"implemented": False, "message": "Crop controls are reserved for the next image pipeline step."},
        "fit_modes": ["contain", "fill", "center"],
    }


def default_image_adjustment_metadata() -> dict:
    return {
        "brightness": 0,
        "contrast": 0,
        "crop": None,
        "fit_mode": "contain",
    }
