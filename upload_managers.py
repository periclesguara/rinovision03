import openai
import os

# Chave direto no código (temporário e só local)
client = openai.OpenAI(api_key="REDACTED_OPENAI_KEY")

arquivos = [
    "managers/audio_manager.py",
    "managers/record_manager.py",
    "managers/scene_manager.py",
    "managers/editor_manager/export_manager.py",
    "managers/editor_manager/music_manager.py",
    "managers/editor_manager/subtitle_manager.py",
    "managers/editor_manager/text_effects_manager.py"
]

for path in arquivos:
    try:
        with open(path, "rb") as f:
            uploaded = client.files.create(file=f, purpose="assistants")
            print(f"✅ {path} => {uploaded.id}")
    except Exception as e:
        print(f"❌ Erro ao enviar {path}: {e}")
