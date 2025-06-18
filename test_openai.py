from src.components.openai_client import gerar_resposta

mensagem = "Você é o sistema RinoVision, se apresente!"
resposta = gerar_resposta(mensagem)

print("\n🎙️ Resposta da IA:")
print(resposta)
