"""Optional network smoke test for the OpenAI integration."""

from src.components.openai_client import gerar_resposta


if __name__ == "__main__":
    print(gerar_resposta("Apresente o protótipo RinoVision em uma frase."))
