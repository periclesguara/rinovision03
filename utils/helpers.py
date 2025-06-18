from datetime import timedelta
import os


def format_time(seconds: int) -> str:
    """
    Converte segundos em string no formato MM:SS.
    """
    return str(timedelta(seconds=seconds))[2:7]


def log(message: str, level="INFO"):
    """
    Print bonito e padronizado no terminal.
    """
    icons = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️", "DEBUG": "🐞"}
    icon = icons.get(level.upper(), "ℹ️")
    print(f"{icon} [{level.upper()}] {message}")


def check_path_exists(path: str) -> bool:
    """
    Verifica se um arquivo ou pasta existe.
    """
    return os.path.exists(path)


def seconds_to_hhmmss(seconds: int) -> str:
    """
    Converte segundos em formato HH:MM:SS.
    """
    return str(timedelta(seconds=seconds))


def safe_filename(filename: str) -> str:
    """
    Gera um nome de arquivo seguro (sem caracteres inválidos).
    """
    return "".join(
        c for c in filename if c.isalnum() or c in (" ", ".", "_", "-")
    ).rstrip()
