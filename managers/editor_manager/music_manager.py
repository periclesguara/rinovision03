# Criar o arquivo music_manager.py com o conteúdo refatorado solicitado
music_manager_code = """
# managers/editor_manager/music_manager.py

import os
import subprocess


def inserir_musica_de_fundo(video_path: str, music_path: str, output_path: str = "output/video_com_musica.mp4", volume_musica: float = 0.2) -> str:
    \"""
    Insere uma música de fundo no vídeo, ajustando o volume da música.

    Parâmetros:
    ----------
    video_path : str
        Caminho para o vídeo original.
    music_path : str
        Caminho para a música de fundo.
    output_path : str
        Caminho do vídeo final com música embutida.
    volume_musica : float
        Volume da música de fundo (entre 0.0 e 1.0).

    Retorna:
    -------
    str
        Caminho do vídeo gerado.
    \"""
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"[music_manager] Vídeo não encontrado: {video_path}")

    if not os.path.exists(music_path):
        raise FileNotFoundError(f"[music_manager] Música não encontrada: {music_path}")

    print("🎵 [music_manager] Inserindo música de fundo no vídeo...")

    try:
        subprocess.call([
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", music_path,
            "-filter_complex", f"[1:a]volume={volume_musica}[bg];[0:a][bg]amix=inputs=2:duration=first:dropout_transition=2[a]",
            "-map", "0:v",
            "-map", "[a]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            output_path
        ])
        print(f"✅ [music_manager] Música inserida com sucesso: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ [music_manager] Erro ao inserir música: {e}")
        return ""
"""

music_file_path = "/mnt/data/music_manager.py"
with open(music_file_path, "w", encoding="utf-8") as f:
    f.write(music_manager_code)

music_file_path
