import os
from functools import lru_cache

from openai import OpenAI


@lru_cache(maxsize=1)
def get_client() -> OpenAI:
    """Create one SDK client using OPENAI_API_KEY from the environment."""
    return OpenAI()


def gerar_resposta(
    mensagem_usuario: str,
    *,
    client: OpenAI | None = None,
    model: str | None = None,
) -> str:
    """Generate text through the Responses API.

    The optional client makes the function testable without a network call.
    Runtime authentication remains the SDK default: OPENAI_API_KEY.
    """
    prompt = mensagem_usuario.strip()
    if not prompt:
        raise ValueError("mensagem_usuario não pode ser vazia")

    sdk = client or get_client()
    response = sdk.responses.create(
        model=model or os.getenv("OPENAI_MODEL", "gpt-5.6"),
        input=prompt,
    )
    return response.output_text
