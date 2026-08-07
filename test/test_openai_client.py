from types import SimpleNamespace

import pytest

from src.components.openai_client import gerar_resposta


class FakeResponses:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(output_text="resposta offline")


def test_gerar_resposta_uses_injected_client():
    responses = FakeResponses()
    client = SimpleNamespace(responses=responses)

    result = gerar_resposta("Olá", client=client, model="test-model")

    assert result == "resposta offline"
    assert responses.calls == [{"model": "test-model", "input": "Olá"}]


def test_gerar_resposta_rejects_empty_prompt():
    with pytest.raises(ValueError):
        gerar_resposta("   ", client=SimpleNamespace())
