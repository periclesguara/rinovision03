import os


def get_log_level() -> str:
    return os.getenv("RINOVISION_LOG_LEVEL", "INFO")


def get_provider_name(default: str = "local_stub") -> str:
    return os.getenv("RINOVISION_PROVIDER", default)
