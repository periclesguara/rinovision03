import os
from openai import OpenAI
from dotenv import load_dotenv

# Carrega as variáveis do .env
load_dotenv()

# Pega a chave da API
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("⚠️ OPENAI_API_KEY não encontrada. Verifique o arquivo .env.")

# Cria o cliente OpenAI
client = OpenAI(api_key=api_key)

def gerar_resposta(mensagem_usuario: str) -> str:
    try:
        resposta = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": mensagem_usuario}],
            temperature=0.7
        )
        return resposta.choices[0].message.content
    except Exception as e:
        return f"[ERRO] Falha ao chamar a OpenAI API: {e}"
