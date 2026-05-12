import os
import subprocess
from pathlib import Path


def inserir_musica_de_fundo(
    video_path: str,
    music_path: str,
    output_path: str = "output/video_com_musica.mp4",
    volume_musica: float = 0.2,
) -> str:
    """
    Insere uma musica de fundo no video usando ffmpeg.

    This legacy helper is intentionally side-effect free at import time. It only
    validates paths and invokes ffmpeg when called explicitly.
    """
    video = Path(video_path)
    music = Path(music_path)
    output = Path(output_path)

    if not video.exists():
        raise FileNotFoundError(f"[music_manager] Video nao encontrado: {video}")
    if not music.exists():
        raise FileNotFoundError(f"[music_manager] Musica nao encontrada: {music}")
    if not 0.0 <= volume_musica <= 1.0:
        raise ValueError("[music_manager] volume_musica deve estar entre 0.0 e 1.0")

    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(video),
        "-i",
        str(music),
        "-filter_complex",
        f"[1:a]volume={volume_musica}[bg];[0:a][bg]amix=inputs=2:duration=first:dropout_transition=2[a]",
        "-map",
        "0:v",
        "-map",
        "[a]",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-shortest",
        str(output),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "[music_manager] ffmpeg failed")
    return str(output)


if __name__ == "__main__":
    print("music_manager is a library module. Import it and call inserir_musica_de_fundo(...).")
