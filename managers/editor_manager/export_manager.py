# managers/editor_manager/export_manager.py

import os
import subprocess


def exportar_video(
    video_path: str,
    legenda_path: str = None,
    trilha_sonora: str = None,
    output_path: str = "output/gravacao_editada.mp4",
) -> str:
    """
    Exporta o vídeo final, opcionalmente adicionando legenda e música de fundo.

    Parâmetros:
    ----------
    video_path : str
        Caminho para o vídeo base (gerado previamente).
    legenda_path : str, opcional
        Caminho para arquivo de legenda (formato .srt).
    trilha_sonora : str, opcional
        Caminho para arquivo de áudio/música a ser embutido.
    output_path : str
        Caminho final de exportação.

    Retorna:
    -------
    str
        Caminho do arquivo de saída gerado.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"[export_manager] Vídeo não encontrado: {video_path}")

    print("🎬 [export_manager] Exportando vídeo final...")

    comandos = ["ffmpeg", "-y", "-i", video_path]

    # Adiciona legenda (opcional)
    if legenda_path and os.path.exists(legenda_path):
        comandos += ["-vf", f"subtitles={legenda_path}"]

    # Adiciona trilha sonora (opcional)
    if trilha_sonora and os.path.exists(trilha_sonora):
        comandos += [
            "-i",
            trilha_sonora,
            "-map",
            "0:v",
            "-map",
            "1:a",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
        ]
    else:
        comandos += ["-c:v", "copy", "-c:a", "aac"]

    comandos += [output_path]

    try:
        subprocess.call(comandos)
        print(f"✅ [export_manager] Exportação concluída: {output_path}")
        return output_path
    except Exception as e:
        print(f"❌ [export_manager] Erro durante exportação: {e}")
        return ""
