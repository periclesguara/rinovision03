import openai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=api_key)

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
