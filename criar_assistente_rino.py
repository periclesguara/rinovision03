import openai
import os

# Inicializa o cliente OpenAI com a chave do projeto (GPT-4o)
client = openai.OpenAI(
    api_key="REDACTED_OPENAI_KEY"
)

assistant = client.beta.assistants.create(
    name="RinoVision",
    instructions="Você é um assistente que ajuda a melhorar e revisar um sistema chamado RinoVision, feito em Python, usando PySide6 e OpenCV.",
    tools=[{"type": "code_interpreter"}],
    model="gpt-4o"
)

print("🧠 Assistente RinoVision criado!")
print("ID do Assistente:", assistant.id)
