import os
import openai

# Sua chave secreta do projeto
API_KEY = "REDACTED_OPENAI_KEY"
ASSISTANT_ID = "asst_ZjIxPl1TwH06KM52fBPL0qar"  # ID do seu assistente

client = openai.OpenAI(api_key=API_KEY)

# Pastas relevantes para subir
pastas = [
    "src",
    "components",
    "utils",
    "gui",
    "scripts",
    "test",
    "path"
]

def coletar_arquivos_python():
    arquivos = []
    for pasta in pastas:
        for root, _, files in os.walk(pasta):
            for file in files:
                if file.endswith(".py"):
                    arquivos.append(os.path.join(root, file))
    return arquivos

def subir_arquivos(arquivos):
    for path in arquivos:
        try:
            with open(path, "rb") as f:
                file = client.files.create(file=f, purpose="assistants")
                print(f"✅ {path} => {file.id}")
                
                # Associa o arquivo ao assistente
                client.beta.assistants.update(
                    assistant_id=ASSISTANT_ID,
                    file_ids=[file.id]
                )
        except Exception as e:
            print(f"❌ Erro ao subir {path}: {e}")

if __name__ == "__main__":
    print("🔍 Coletando arquivos .py das pastas...")
    arquivos = coletar_arquivos_python()
    print(f"📁 {len(arquivos)} arquivos encontrados.")
    subir_arquivos(arquivos)
