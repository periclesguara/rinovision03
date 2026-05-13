import openai
import os

client = openai.OpenAI(api_key="REDACTED_OPENAI_KEY")

# Lista de arquivos que você quer associar
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

# Cria um vector store novo
vector_store = client.beta.vector_stores.create(name="Arquivos RinoVision")
print(f"📦 Vector Store criado: {vector_store.id}")

# Faz upload dos arquivos
file_ids = []
for path in arquivos:
    try:
        with open(path, "rb") as f:
            uploaded = client.files.create(file=f, purpose="assistants")
            file_ids.append(uploaded.id)
            print(f"✅ Enviado: {path} => {uploaded.id}")
    except Exception as e:
        print(f"❌ Erro ao enviar {path}: {e}")

# Associa os arquivos ao vector store
if file_ids:
    client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id,
        files=file_ids
    )
    print(f"🧠 Arquivos vinculados ao vector store {vector_store.id}")

# Atualiza o assistente com o vector store
ASSISTANT_ID = "asst_8HnlJbt9icIEKfefftzXINQC"

client.beta.assistants.update(
    assistant_id=ASSISTANT_ID,
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}}
)

print(f"🔗 Assistente {ASSISTANT_ID} atualizado com os arquivos.")
