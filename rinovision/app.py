from .paths import ensure_data_dirs


def bootstrap() -> str:
    ensure_data_dirs()
    return "RinoVision foundation ready"
