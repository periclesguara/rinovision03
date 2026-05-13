import openai
import os

client = openai.OpenAI(api_key="REDACTED_OPENAI_KEY")

# Substitua com o ID que apareceu ao criar o assistente
ASSISTANT_ID = "asst_8HnlJbt9icIEKfefftzXINQC"

# Lista de arquivos que você quer anexar
arquivos = [
    "windows/base_window.py",
    "windows/compositor_window.py",
    "windows/edition_window.py",
    "windows/image_composer_window.py",
    "managers/scene_manager.py",
    "managers/record_manager.py",
    "managers/audio_manager.py",
    "managers/editor_manager/export_manager.py",
    "managers/editor_manager/music_manager.py",
    "managers/editor_manager/subtitle_manager.py",
    "managers/editor_manager/text_effects_manager.py"
]

for caminho in arquivos:
    try:
        with open(caminho, "rb") as f:
            uploaded_file = client.files.create(file=f, purpose="assistants")
            client.beta.assistants.update(
                assistant_id=ASSISTANT_ID,
                tool_resources={
                    "file_search": {
                        "vector_store": {
                            "file_ids": [uploaded_file.id]
                        }
                    }
                }
            )
            print(f"✅ {caminho} anexado ao assistente.")
    except Exception as e:
        print(f"❌ Erro ao anexar {caminho}: {e}")
