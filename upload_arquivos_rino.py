import os
import openai

# 🔑 Sua chave secreta aqui
client = openai.OpenAI(
    api_key="REDACTED_OPENAI_KEY"
)

# 🗂 Pastas raiz para varredura
pastas = [
    "managers", "windows", "utils", "components", "gui", "src", "test"
]

print("🔍 Coletando arquivos .py das pastas...")

arquivos_py = []

for pasta in pastas:
    for raiz, _, arquivos in os.walk(pasta):
        for arquivo in arquivos:
            if arquivo.endswith(".py"):
                caminho = os.path.join(raiz, arquivo)
                if os.path.getsize(caminho) > 0:  # Ignora arquivos vazios
                    arquivos_py.append(caminho)

print(f"📁 {len(arquivos_py)} arquivos encontrados.")

for caminho in arquivos_py:
    try:
        with open(caminho, "rb") as f:
            response = client.files.create(file=f, purpose="assistants")
            print(f"✅ {caminho} => {response.id}")
    except Exception as e:
        print(f"❌ Erro ao subir {caminho}: {e}")
