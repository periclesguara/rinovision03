# managers/editor_manager/subtitle_manager.py

import os
import tempfile
import subprocess


def gerar_legenda(audio_path: str) -> str:
    """
    Gera uma legenda em formato texto a partir de um arquivo de áudio (.wav).

    Parâmetros:
    ----------
    audio_path : str
        Caminho completo para o arquivo de áudio.

    Retorna:
    -------
    str
        Texto da legenda extraída (ou string vazia se falhar).
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(
            f"[subtitle_manager] Arquivo não encontrado: {audio_path}"
        )

    print(f"🎙️ [subtitle_manager] Iniciando geração de legenda para: {audio_path}")

    # Cria diretório e nome temporário para salvar a transcrição
    base_dir = os.path.dirname(audio_path)
    filename_base = os.path.splitext(os.path.basename(audio_path))[0]
    output_txt = os.path.join(base_dir, f"{filename_base}.txt")

    try:
        subprocess.call(
            [
                "whisper",
                audio_path,
                "--model",
                "base",
                "--language",
                "pt",
                "--output_format",
                "txt",
                "--output_dir",
                base_dir,
            ]
        )

        if os.path.exists(output_txt):
            with open(output_txt, "r", encoding="utf-8") as f:
                legenda = f.read()
            print("✅ [subtitle_manager] Legenda gerada com sucesso.")
            return legenda
        else:
            print("⚠️ [subtitle_manager] Legenda não foi gerada.")
            return ""

    except Exception as e:
        print(f"❌ [subtitle_manager] Erro na geração de legenda: {e}")
        return ""
